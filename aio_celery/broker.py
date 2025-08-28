from __future__ import annotations

from typing import TYPE_CHECKING
import aio_pika

if TYPE_CHECKING:
    from aio_pika.abc import (
        AbstractQueue,
        AbstractRobustChannel,
    )
    from pamqp.common import Arguments


class Broker:
    def __init__(
        self,
        *,
        broker_url: str,
        task_queue_max_priority: int | None,
        broker_publish_timeout: float | None,
        publishing_channel: AbstractRobustChannel,
        exchange_name: str,
        routing_key: str,
        dead_letter_exchange: str | None = None,
        consumer_ack_timeout: int | None = None,
        exchange_type: aio_pika.ExchangeType = aio_pika.ExchangeType.DIRECT,
        exchange_durable: bool = True,
    ) -> None:
        self._broker_url = broker_url
        self._task_queue_max_priority: int | None = task_queue_max_priority
        self._already_declared_queues: set[str] = set()
        self._broker_publish_timeout = broker_publish_timeout
        self._publishing_channel = publishing_channel
        self._dead_letter_exchange = dead_letter_exchange
        self._consumer_ack_timeout = consumer_ack_timeout
        self._is_client = False
        self._exchange = None
        self._exchange_name = exchange_name
        self._routing_key = routing_key
        self._exchange_type = exchange_type
        self._exchange_durable = exchange_durable

    def set_client(self) -> None:
        self._is_client = True

    async def publish_message(
        self,
        message: aio_pika.Message,
        *,
        routing_key: str,
    ) -> None:
        # app with different types of queues, we dont want to declare the queue, they each have their own rabbit config.
        # so dont declare queues unless we are in the worker.  im totally ok with errors
        # i know this is a decoupling of the concepts now.  but some queues need to wait a long time
        if not self._is_client and routing_key not in self._already_declared_queues:
            await self.declare_queue(
                queue_name=routing_key,
                channel=self._publishing_channel,
                dlx=self._dead_letter_exchange,
                ack_timeout=self._consumer_ack_timeout,
            )

        await self._publishing_channel.default_exchange.publish(
            message,
            routing_key=routing_key,
            timeout=self._broker_publish_timeout,
        )

    async def declare_queue(
        self,
        *,
        queue_name: str,
        channel: AbstractRobustChannel,
    ) -> AbstractQueue:
        arguments: Arguments = {}
        if self._exchange is None:
            self._exchange = await channel.declare_exchange(
                self._exchange_name,
                self._exchange_type,
                durable=self._exchange_durable,
            )
        if self._task_queue_max_priority is not None:
            arguments["x-max-priority"] = self._task_queue_max_priority
            
        if self._dead_letter_exchange is not None:
            arguments["x-dead-letter-exchange"] = self._dead_letter_exchange
            arguments["x-dead-letter-routing-key"] = f"{queue_name}.dead_letter"
            
        if self._consumer_ack_timeout is not None:
            # Convert seconds to milliseconds for x-consumer-timeout
            arguments["x-consumer-timeout"] = self._consumer_ack_timeout * 1000
            
        queue = await channel.declare_queue(
            name=queue_name,
            durable=True,
            arguments=arguments if arguments else None,
            timeout=self._broker_publish_timeout,
        )
        await queue.bind(self._exchange, routing_key=self._routing_key)
        self._already_declared_queues.add(queue_name)
        return queue

"""Configuration RabbitMQ pour les évènements et notifications."""
import logging
from typing import Optional, Callable, Any
import json
from aio_pika import connect_robust, Message, ExchangeType
from aio_pika.abc import AbstractRobustConnection, AbstractChannel, AbstractExchange, AbstractQueue
from core.config import settings

logger = logging.getLogger(__name__)

class RabbitMQ:
    """Gestionnaire RabbitMQ pour les évènements."""

    connection: Optional[AbstractRobustConnection] = None
    channel: Optional[AbstractChannel] = None
    exchanges: dict[str, AbstractExchange] = {}
    queues: dict[str, AbstractQueue] = {}

    async def connect(self) -> None:
        """Etablit la connexion à RabbitMQ."""
        self.connection = await connect_robust(settings.rabbitmq_url)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=10)

        # Créer les exchanges principaux
        await self._setup_exchanges()
        logger.info("Connecté à RabbitMQ")

    async def _setup_exchanges(self) -> None:
        """Configure les exchanges de base."""
        if not self.channel:
            return

        # Exchange pour les notifications
        self.exchanges["notifications"] = await self.channel.declare_exchange(
            "notifications",
            ExchangeType.TOPIC,
            durable=True
        )

        # Exchange pour les évènements métier
        self.exchanges["events"] = await self.channel.declare_exchange(
            "events",
            ExchangeType.TOPIC,
            durable=True
        )

        # Exchange pour les commandes asynchrones
        self.exchanges["commands"] = await self.channel.declare_exchange(
            "commands",
            ExchangeType.DIRECT,
            durable=True
        )

    async def disconnect(self) -> None:
        """Ferme la connexion à RabbitMQ."""
        if self.connection:
            await self.connection.close()
            logger.info("= Déconnecté de RabbitMQ")

    async def publish(
        self,
        exchange_name: str,
        routing_key: str,
        message: dict[str, Any]
    ) -> None:
        """
        Publie un message dans un exchange.

        Args:
            exchange_name: Nom de l'exchange
            routing_key: Clé de routage
            message: Dictionnaire à publier
        """
        if not self.channel or exchange_name not in self.exchanges:
            raise RuntimeError(f"Exchange {exchange_name} not found")

        exchange = self.exchanges[exchange_name]
        message_body = json.dumps(message).encode()

        await exchange.publish(
            Message(
                body=message_body,
                content_type="application/json",
                delivery_mode=2  # Persistent
            ),
            routing_key=routing_key
        )

    async def declare_queue(
        self,
        queue_name: str,
        exchange_name: str,
        routing_key: str,
        durable: bool = True
    ) -> AbstractQueue:
        """
        Déclare une queue et la bind à un exchange.

        Args:
            queue_name: Nom de la queue
            exchange_name: Nom de l'exchange
            routing_key: Clé de routage
            durable: Queue persistante
        """
        if not self.channel or exchange_name not in self.exchanges:
            raise RuntimeError(f"Exchange {exchange_name} not found")

        queue = await self.channel.declare_queue(
            queue_name,
            durable=durable
        )

        await queue.bind(
            self.exchanges[exchange_name],
            routing_key=routing_key
        )

        self.queues[queue_name] = queue
        return queue

    async def consume(
        self,
        queue_name: str,
        callback: Callable
    ) -> None:
        """
        Consomme les messages d'une queue.

        Args:
            queue_name: Nom de la queue
            callback: Fonction async à appeler pour chaque message
        """
        if queue_name not in self.queues:
            raise RuntimeError(f"Queue {queue_name} not declared")

        queue = self.queues[queue_name]

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        body = json.loads(message.body.decode())
                        await callback(body)
                    except Exception as e:
                        logger.info(f"L Error processing message: {e}")


rabbitmq = RabbitMQ()


async def get_rabbitmq() -> RabbitMQ:
    """Dependency pour obtenir RabbitMQ."""
    return rabbitmq

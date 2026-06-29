import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from config import BOT_TOKEN, ADMIN_ID
from bot.handlers import router, send_daily_report

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создаём бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Подключаем обработчики
dp.include_router(router)

# Функция для отправки отчёта каждый день в 9:00
async def schedule_daily_report():
    """Envía el informe todos los días a las 9:00."""
    while True:
        now = datetime.now()
        target = datetime(now.year, now.month, now.day, 9, 0)
        
        if now > target:
            target = target.replace(day=target.day + 1)
        
        wait_seconds = (target - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        
        try:
            await send_daily_report()
        except Exception as e:
            logger.error(f"Error al enviar el informe: {e}")

# Запуск
async def main():
    logger.info("🚀 ¡Bot Lera iniciado!")
    logger.info("📦 Comandos disponibles: /inicio, /diario, /menu, /estadisticas, /perfil, /ayuda, /cancelar_solicitud")
    
    # Запускаем планировщик отчётов
    asyncio.create_task(schedule_daily_report())
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot detenido")
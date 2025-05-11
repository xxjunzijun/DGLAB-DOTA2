import asyncio
import io
import qrcode
import socket
from aiohttp import web
from pydglab_ws import StrengthData, FeedbackButton, Channel, RetCode, DGLabWSServer, StrengthOperationType
import time

PULSE_DATA = {
    '呼吸': [
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 5, 10, 20)),
        ((10, 10, 10, 10), (20, 25, 30, 40)), ((10, 10, 10, 10), (40, 45, 50, 60)),
        ((10, 10, 10, 10), (60, 65, 70, 80)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((0, 0, 0, 0), (0, 0, 0, 0)), ((0, 0, 0, 0), (0, 0, 0, 0)), ((0, 0, 0, 0), (0, 0, 0, 0))
    ],
    '潮汐': [
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 4, 8, 17)),
        ((10, 10, 10, 10), (17, 21, 25, 33)), ((10, 10, 10, 10), (50, 50, 50, 50)),
        ((10, 10, 10, 10), (50, 54, 58, 67)), ((10, 10, 10, 10), (67, 71, 75, 83)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (100, 98, 96, 92)),
        ((10, 10, 10, 10), (92, 90, 88, 84)), ((10, 10, 10, 10), (84, 82, 80, 76)),
        ((10, 10, 10, 10), (68, 68, 68, 68))
    ],
    '连击': [
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (0, 0, 0, 0)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (100, 92, 84, 67)),
        ((10, 10, 10, 10), (67, 58, 50, 33)), ((10, 10, 10, 10), (0, 0, 0, 0)),
        ((10, 10, 10, 10), (0, 0, 0, 1)), ((10, 10, 10, 10), (2, 2, 2, 2))
    ],
    '快速按捏': [
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((0, 0, 0, 0), (0, 0, 0, 0))
    ],
    '按捏渐强': [
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (29, 29, 29, 29)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (52, 52, 52, 52)),
        ((10, 10, 10, 10), (2, 2, 2, 2)), ((10, 10, 10, 10), (73, 73, 73, 73)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (87, 87, 87, 87)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (0, 0, 0, 0))
    ],
    '心跳节奏': [
        ((110, 110, 110, 110), (100, 100, 100, 100)), ((110, 110, 110, 110), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 0, 0, 0)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 0, 0, 0)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (75, 75, 75, 75)),
        ((10, 10, 10, 10), (75, 77, 79, 83)), ((10, 10, 10, 10), (83, 85, 88, 92)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (0, 0, 0, 0)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 0, 0, 0)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 0, 0, 0))
    ],
    '压缩': [
        ((25, 25, 24, 24), (100, 100, 100, 100)), ((24, 23, 23, 23), (100, 100, 100, 100)),
        ((22, 22, 22, 21), (100, 100, 100, 100)), ((21, 21, 20, 20), (100, 100, 100, 100)),
        ((20, 19, 19, 19), (100, 100, 100, 100)), ((18, 18, 18, 17), (100, 100, 100, 100)),
        ((17, 16, 16, 16), (100, 100, 100, 100)), ((15, 15, 15, 14), (100, 100, 100, 100)),
        ((14, 14, 13, 13), (100, 100, 100, 100)), ((13, 12, 12, 12), (100, 100, 100, 100)),
        ((11, 11, 11, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (100, 100, 100, 100))
    ],
    '节奏步伐': [
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 5, 10, 20)),
        ((10, 10, 10, 10), (20, 25, 30, 40)), ((10, 10, 10, 10), (40, 45, 50, 60)),
        ((10, 10, 10, 10), (60, 65, 70, 80)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 6, 12, 25)),
        ((10, 10, 10, 10), (25, 31, 38, 50)), ((10, 10, 10, 10), (50, 56, 62, 75)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (0, 0, 0, 0)),
        ((10, 10, 10, 10), (0, 8, 16, 33)), ((10, 10, 10, 10), (33, 42, 50, 67)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (0, 0, 0, 0)),
        ((10, 10, 10, 10), (0, 12, 25, 50)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (100, 100, 100, 100))
    ],
    '颗粒摩擦': [
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (0, 0, 0, 0))
    ],
    '渐变弹跳': [
        ((10, 10, 10, 10), (1, 1, 1, 1)), ((10, 10, 10, 10), (1, 9, 18, 34)),
        ((10, 10, 10, 10), (34, 42, 50, 67)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((0, 0, 0, 0), (0, 0, 0, 0)), ((0, 0, 0, 0), (0, 0, 0, 0))
    ],
    '波浪涟漪': [
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 12, 25, 50)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (73, 73, 73, 73))
    ],
    '雨水冲刷': [
        ((10, 10, 10, 10), (34, 34, 34, 34)), ((10, 10, 10, 10), (34, 42, 50, 67)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((0, 0, 0, 0), (0, 0, 0, 0)),
        ((0, 0, 0, 0), (0, 0, 0, 0))
    ],
    '变速敲击': [
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (0, 0, 0, 0)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 0, 0, 0)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((110, 110, 110, 110), (100, 100, 100, 100)),
        ((110, 110, 110, 110), (100, 100, 100, 100)), ((110, 110, 110, 110), (100, 100, 100, 100)),
        ((110, 110, 110, 110), (100, 100, 100, 100)), ((0, 0, 0, 0), (0, 0, 0, 0))
    ],
    '信号灯': [
        ((197, 197, 197, 197), (100, 100, 100, 100)), ((197, 197, 197, 197), (100, 100, 100, 100)),
        ((197, 197, 197, 197), (100, 100, 100, 100)), ((197, 197, 197, 197), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 8, 16, 33)),
        ((10, 10, 10, 10), (33, 42, 50, 67)), ((10, 10, 10, 10), (100, 100, 100, 100))
    ],
    '挑逗1': [
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 6, 12, 25)),
        ((10, 10, 10, 10), (25, 31, 38, 50)), ((10, 10, 10, 10), (50, 56, 62, 75)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (0, 0, 0, 0)),
        ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 0, 0, 0)), ((10, 10, 10, 10), (0, 0, 0, 0)),
        ((10, 10, 10, 10), (100, 100, 100, 100))
    ],
    '挑逗2': [
        ((10, 10, 10, 10), (1, 1, 1, 1)), ((10, 10, 10, 10), (1, 4, 6, 12)),
        ((10, 10, 10, 10), (12, 15, 18, 23)), ((10, 10, 10, 10), (23, 26, 28, 34)),
        ((10, 10, 10, 10), (34, 37, 40, 45)), ((10, 10, 10, 10), (45, 48, 50, 56)),
        ((10, 10, 10, 10), (56, 59, 62, 67)), ((10, 10, 10, 10), (67, 70, 72, 78)),
        ((10, 10, 10, 10), (78, 81, 84, 89)), ((10, 10, 10, 10), (100, 100, 100, 100)),
        ((10, 10, 10, 10), (100, 100, 100, 100)), ((10, 10, 10, 10), (0, 0, 0, 0)),
        ((0, 0, 0, 0), (0, 0, 0, 0))
    ]
}

def get_local_address():
    """获取本机IP地址"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    localAddr = s.getsockname()[0]
    s.close()
    print(f"获取到本机地址: {localAddr}")
    return localAddr

def print_qrcode(data: str):
    """输出二维码到终端界面"""
    qr = qrcode.QRCode()
    qr.add_data(data)
    f = io.StringIO()
    qr.print_ascii(out=f)
    f.seek(0)
    print(f.read())

QUEUE_MSG_DGLAB = 1
QUEUE_MSG_HERO_GET_DAMAGE = 2
QUEUE_MSG_HERO_COOL_DOWN = 3
QUEUE_MSG_HERO_CLEAR_PULSE = 4

class queueMsg:
    def __init__(self):
        self.msgType = 0
        self.msgData = []

class Application:
    def __init__(self):
        self.dglab_ready = asyncio.Event()
        self.app = web.Application()
        self.dataQueue = asyncio.Queue(maxsize=100)
        self.runner = None
        self.site = None
        # dglab
        self.channelAMax = 0
        self.channelBMax = 0
        self.channelACur = 0
        self.channelBCur = 0
        self.pulseDataIter = iter(PULSE_DATA.values())
        # hero data
        self.heroLastHealth = 0
        self.heroCurDamage = 0
        self.coolDownCnt = 0
        # rate limit
        self.lastDateTime = 0

    def allow_add_pulse(self):
        millis = int(time.time() * 1000) # 获取当前时间戳
        timeGap = millis - self.lastDateTime
        if timeGap > 100:
            self.lastDateTime = millis
            return True
        else:
            return False
        
    async def dglab_add_pulse(self, count, client):
        curPulse = next(self.pulseDataIter, None) 
        if not curPulse:
            self.pulseDataIter = iter(PULSE_DATA.values())
            curPulse = next(self.pulseDataIter, None)
        await client.add_pulses(Channel.A, *(curPulse * count))
        await client.add_pulses(Channel.B, *(curPulse * count))
        millis = int(time.time() * 1000)

    async def dglab_set_strength_add(self, increaseNum, client):
        increaseAMax = self.channelAMax - self.channelACur
        increaseBMax = self.channelBMax - self.channelBCur
        increaseA = min(increaseAMax, increaseNum)
        increaseB = min(increaseBMax, increaseNum)
        if increaseA != 0:
            await client.set_strength(Channel.A, StrengthOperationType.INCREASE, increaseA)
        if increaseB != 0:
            await client.set_strength(Channel.B, StrengthOperationType.INCREASE, increaseB)

    async def process_queue_data(self, client):
        """从队列中获取并处理数据"""
        while True:
            try:
                # 从队列获取数据）
                data = await self.dataQueue.get()
                msgType = data.msgType
                if msgType == QUEUE_MSG_DGLAB: # 更新强度信息
                    self.channelACur = data.msgData[0]
                    self.channelAMax = data.msgData[1]
                    self.channelBCur = data.msgData[2]
                    self.channelBMax = data.msgData[3]
                    print(f"获取到最新通道强度:\nA: {self.channelACur}/{self.channelAMax}   B: {self.channelBCur}/{self.channelBMax}")
                elif msgType == QUEUE_MSG_HERO_GET_DAMAGE:
                    if self.allow_add_pulse():  # 限制短时间内发送的脉冲次数
                        await self.dglab_add_pulse(1, client)  # 每受到伤害触发一次电击
                    damage = data.msgData[0]
                    damage += self.heroCurDamage
                    increase = int(damage / 100)  # 每累计100伤害，强度+1
                    left = damage % 100
                    await self.dglab_set_strength_add(increase, client)
                    self.heroCurDamage = left   # 重置累计伤害
                elif msgType == QUEUE_MSG_HERO_COOL_DOWN:
                    await client.set_strength(Channel.A, StrengthOperationType.DECREASE, 1)
                    await client.set_strength(Channel.B, StrengthOperationType.DECREASE, 1)
                elif msgType == QUEUE_MSG_HERO_CLEAR_PULSE:
                    await client.clear_pulses(Channel.A)
                    await client.clear_pulses(Channel.B)
                else:
                    print("=======队列收到异常信息========")
                self.dataQueue.task_done()
            except Exception as e:
                print(f"处理队列数据出错: {e}")

    async def get_hero_data_enque(self, request):
        """获取英雄数据并将英雄数据写入队列"""
        data = await request.json()
        try:
            msg = queueMsg()
            hero = data.get("hero", {})
            curHealth = hero.get("health")   # 当前生命值
            lastHealth = self.heroLastHealth  # 上一次获取的生命值
            damage = lastHealth - curHealth # 获取收到伤害量
            self.heroLastHealth = curHealth # 更新当前血量
            if damage >= 50:    # 单次伤害超过50才会触发
                msg.msgType = QUEUE_MSG_HERO_GET_DAMAGE
                msg.msgData = [damage]
                self.coolDownCnt = 0
                await self.dataQueue.put(msg)
            else:
                self.coolDownCnt += 1
                if self.coolDownCnt == 10: # 防止送入太多脉冲导致没受到伤害后还会被电
                    msg.msgType = QUEUE_MSG_HERO_CLEAR_PULSE
                    await self.dataQueue.put(msg)
                if self.coolDownCnt >= 30:  # 长时间没受到伤害,减少强度
                    msg.msgType = QUEUE_MSG_HERO_COOL_DOWN
                    self.coolDownCnt = 0
                    await self.dataQueue.put(msg)
        except Exception as e:
            print("本次解析英雄数据失败，忽略")
        return web.json_response({"status": "success"})

    async def dglab_service(self):
        """主服务端，用于与郊狼交互"""
        async with DGLabWSServer("0.0.0.0", 5678, 60) as server:
            client = server.new_local_client()
            
            # 生成连接二维码
            localAddr = get_local_address()
            url = client.get_qrcode(f"ws://{localAddr}:5678")
            print("请用 DG-Lab App 扫描二维码以连接")
            print_qrcode(url)
            
            # 等待绑定
            await client.bind()
            print(f"已与 App {client.target_id} 成功绑定")
            
            # DG-Lab 连接后，再去启动web服务
            self.dglab_ready.set()
            
            try:
                # 创建数据处理任务
                process_task = asyncio.create_task(self.process_queue_data(client))

                # 主事件循环
                getStrengthData = 0
                async for data in client.data_generator(StrengthData, FeedbackButton, RetCode):
                    if isinstance(data, FeedbackButton):
                        print(f"App 反馈按钮: {data.name}")
                        await self.dglab_add_pulse(1, client)  # 触发一次电击
                    elif isinstance(data, StrengthData):
                        msg = queueMsg()
                        msg.msgType = QUEUE_MSG_DGLAB
                        msg.msgData = [data.a, data.a_limit, data.b, data.b_limit]
                        await self.dataQueue.put(msg)
                    elif data == RetCode.CLIENT_DISCONNECTED:
                        print("App 已断开连接")

            finally:
                process_task.cancel()
                try:
                    await process_task
                except asyncio.CancelledError:
                    pass
                self.dglab_ready.clear()

    async def http_service(self):
        """web服务，用于获取英雄数据"""
        await self.dglab_ready.wait()

        # 配置路由
        self.app.router.add_post('/', self.get_hero_data_enque)

        # 启动 Web 服务
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, '0.0.0.0', 3000)
        await self.site.start()
        print("Web 服务在 3000 端口启动")

    async def run(self):
        """运行所有服务"""
        dglab_task = asyncio.create_task(self.dglab_service())
        http_task = asyncio.create_task(self.http_service())

        await asyncio.gather(dglab_task, http_task)

    async def shutdown(self):
        """关闭服务"""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        print("服务已关闭")

async def start_services():
    app = Application()
    try:
        await app.run()
    except (KeyboardInterrupt, asyncio.CancelledError):
        await app.shutdown()

if __name__ == "__main__":
    asyncio.run(start_services())
    input("输入任意键退出...")
from session_handler import SessionHandler
from downloader import Downloader


if __name__ == '__main__':

    # 获取session
    session = SessionHandler().get_session()
    downloader=Downloader(session)
    # 下载排行榜数据
    downloader.download_image(page=3)
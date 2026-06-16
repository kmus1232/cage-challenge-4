# Copyright DST Group. Licensed under the MIT license.
import sys
import logging
import os.path as osp


class CybORGLogger:
    """A logger class for CybORG.

    It has two main functions:
    1. acts as a wrapper for the Python logger class
    2. provides a base class with useful logging function that other classes
    can inherit and use to make logging easier.

    [한국어]
    CybORG용 로거 클래스. 역할은 두 가지다.
    1. 파이썬 표준 logging 모듈을 감싸는 래퍼(Wrapper) 역할을 한다.
    2. 로깅을 편하게 쓰도록 유용한 로깅 함수를 모아둔 베이스 클래스 역할을 한다.
       다른 클래스가 이 클래스를 상속해 로깅 메서드를 그대로 사용할 수 있다.
    """

    logger_name = "CybORGLog-Process"
    sshtunnel_logger_name = f"{logger_name}-sshtunnel"

    # Add extra levels to logging
    # 표준 로깅 레벨에 더해 커스텀 레벨(DEBUG2)을 추가 등록한다.
    DEBUG2 = "DEBUG2"
    DEBUG2_LVL = logging.DEBUG-1
    logging.addLevelName(DEBUG2_LVL, DEBUG2)

    @staticmethod
    def setup(config, verbosity: int = None):
        """Setup the CybORG logger using given configuration.

        Arguments
        ---------
        config : CybORGConfig
            the configuration object
        verbosity : int, optional
            verbosity level of console logger, if None uses level in config.
            Level 0 = logging.WARNING (30) and above
            Level 1 = logging.INFO (20) and above
            Level 2 = logging.WARNING (10) and above
            Level 3 = CybORGLogger.DEBUG2 (9) and above (i.e. will show
                      messages logged with the debug2() method.
            Level 4+ = logging.NOTSET (0) and above (i.e. will display all
                       logged information)

        [한국어]
        주어진 설정(config)으로 CybORG 로거를 초기화한다.

        인자
        ---------
        config : CybORGConfig
            설정 객체.
        verbosity : int, optional
            콘솔 로거의 상세 출력 수준. None이면 config에 정의된 레벨을 쓴다.
            숫자가 클수록 더 자세한 로그까지 출력한다.
            Level 0 = WARNING(30) 이상만 출력
            Level 1 = INFO(20) 이상 출력
            Level 2 = DEBUG(10) 이상 출력 (원문 주석은 WARNING으로 표기되어
                      있으나 실제 임계값은 10으로 DEBUG 레벨이다)
            Level 3 = DEBUG2(9) 이상 출력 (debug2() 메서드로 남긴 메시지까지 표시)
            Level 4+ = NOTSET(0) 이상, 즉 기록된 모든 로그를 출력
        """
        console_log_level = config.default_console_log_level
        # [설명] verbosity 값에 따라 콘솔 로그 임계 레벨을 역산한다.
        # WARNING=30 기준에서 verbosity*10을 빼므로 0->30, 1->20, 2->10이 되고,
        # 숫자가 클수록 더 낮은(=더 자세한) 레벨까지 출력한다.
        # 3은 커스텀 DEBUG2, 4 이상은 NOTSET(전부 출력)으로 분기한다.
        if verbosity:
            assert verbosity >= 0, "Invalid verbosity, must be >= 0"
            if verbosity <= 2:
                console_log_level = logging.WARNING - verbosity*10
            elif verbosity == 3:
                console_log_level = CybORGLogger.DEBUG2
            else:
                console_log_level = logging.NOTSET

        CybORGLogger.logger_name = config.logger_name
        formatter = logging.Formatter(
            fmt=config.logging_format, datefmt=config.logging_date_format
        )
        console_log_level = logging.getLevelName(console_log_level)
        file_log_level = logging.getLevelName(config.default_file_log_level)
        logger = logging.getLogger(config.logger_name)

        # create console handler
        # 콘솔(표준출력) 핸들러를 생성한다.
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(console_log_level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # set the log level of the logger itself
        # 로거 자체의 로그 레벨을 설정한다.
        logger.setLevel(console_log_level)

        # Do NOT propogate log messages to the root logger
        # 로그 메시지를 루트 로거로 전파하지 않는다(중복 출력 방지).
        logger.propagate = False

        if config.log_to_file:
            log_file = osp.join(config.log_dir_path, config.logger_file_name)
            fh = logging.FileHandler(filename=log_file, mode='w')
            fh.setLevel(file_log_level)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
            logger.setLevel(file_log_level)

        ##################################################################
        # Paramiko logging config
        # Paramiko(SSH 라이브러리) 로깅 설정
        ##################################################################
        import paramiko
        paramiko_logger_name = f"{config.logger_name}-paramiko"
        paramiko_logger = paramiko.util.get_logger("paramiko")
        # Suppress paramiko's verbose output to stdout
        # paramiko의 장황한 출력이 표준출력으로 쏟아지지 않도록 파일로 보낸다.
        paramiko_log_file = osp.join(
            config.log_dir_path, paramiko_logger_name + ".log"
        )
        paramiko.util.log_to_file(paramiko_log_file, level="WARN")
        paramiko_logger.setLevel(logging.WARNING)
        # don't dump on console
        # 콘솔로 출력하지 않는다(전파 차단).
        paramiko_logger.propagate = False

        ##################################################################
        # SSHTunnel logging config
        # SSHTunnel(SSH 터널) 로깅 설정
        ##################################################################
        ssht_log_format = "%(asctime)-15s (%(levelname)-8s) ==> %(message)s"
        ssht_formatter = logging.Formatter(
            fmt=ssht_log_format, datefmt=config.logging_date_format
        )

        # note this is not the default logger name for SSHTunnel,
        # just a name chosen for CybORG
        # 참고: 이건 SSHTunnel의 기본 로거 이름이 아니라 CybORG가 임의로 정한 이름이다.
        sshtunnel_logger_name = f"{config.logger_name}-sshtunnel"
        sshtunnel_logger = logging.getLogger(sshtunnel_logger_name)
        # Don't dump sshtunnel outputs to console
        # sshtunnel 출력을 콘솔로 내보내지 않는다(전파 차단).
        sshtunnel_logger.propagate = False
        if config.log_to_file:
            # create file handler
            # 파일 핸들러를 생성한다.
            ssh_log_file = osp.join(
                config.log_dir_path, sshtunnel_logger_name + ".txt"
            )
            sfh = logging.FileHandler(ssh_log_file, mode='w')
            sfh.setLevel(file_log_level)
            # create formatter and add it to the handlers
            # 포매터를 만들어 핸들러에 붙인다.
            sfh.setFormatter(ssht_formatter)
            # add the handlers to the sshtunnel_logger
            # 핸들러를 sshtunnel_logger에 등록한다.
            sshtunnel_logger.addHandler(sfh)

    @staticmethod
    def setLevel(level):
        logging.getLogger(
            CybORGLogger.logger_name
        ).setLevel(level=level)

    @staticmethod
    def debug(msg, *args, **kwargs):
        logging.getLogger(
            CybORGLogger.logger_name
        ).debug(msg, *args, **kwargs)

    @staticmethod
    def debug2(msg, *args, **kwargs):
        logging.getLogger(
            CybORGLogger.logger_name
        ).log(CybORGLogger.DEBUG2_LVL, msg, *args, **kwargs)

    @staticmethod
    def info(msg, *args, **kwargs):
        logging.getLogger(
            CybORGLogger.logger_name
        ).info(msg, *args, **kwargs)

    @staticmethod
    def warning(msg, *args, **kwargs):
        logging.getLogger(
            CybORGLogger.logger_name
        ).warning(msg, *args, **kwargs)

    @staticmethod
    def error(msg, *args, **kwargs):
        logging.getLogger(
            CybORGLogger.logger_name
        ).error(msg, *args, **kwargs)

    @staticmethod
    def critical(msg, *args, **kwargs):
        logging.getLogger(
            CybORGLogger.logger_name
        ).critical(msg, *args, **kwargs)

    @staticmethod
    def header(title):
        CybORGLogger.info(f"\n\n{'':*^30} {title:^50} {'':*^30}\n\n")

    @staticmethod
    def get_logger():
        return logging.getLogger(CybORGLogger.logger_name)

    @staticmethod
    def get_ssh_tunnel_logger():
        return logging.getLogger(CybORGLogger.sshtunnel_logger_name)

    def _log_header(self, title):
        CybORGLogger.header(self._format_log_msg(title))

    def _log_info(self, msg):
        CybORGLogger.info(self._format_log_msg(msg))

    def _log_error(self, msg):
        CybORGLogger.error(self._format_log_msg(msg))

    def _log_debug(self, msg):
        CybORGLogger.debug(self._format_log_msg(msg))

    def _log_debug2(self, msg):
        CybORGLogger.debug2(self._format_log_msg(msg))

    def _log_warning(self, msg):
        CybORGLogger.warning(self._format_log_msg(msg))

    def _format_log_msg(self, msg):
        """Overide this function for more informative logging messages

        [한국어]
        더 풍부한 로그 메시지가 필요하면 이 메서드를 오버라이드한다.
        기본 동작은 "<클래스 이름>: <메시지>" 형태로 메시지 앞에 클래스명을 붙인다.
        """
        return f"{self.__class__.__name__}: {msg}"


def log_trace(func):
    """Logger decorator for logging function execution.

    Import this function and add @log_trace above your function of
    interest to log output to file about the functions execution

    [한국어]
    함수 실행을 로깅하는 데코레이터.
    이 함수를 import한 뒤 추적하고 싶은 함수 위에 @log_trace를 붙이면,
    그 함수의 실행 정보(진입/인자/종료)가 로그로 남는다.
    """
    def call(*args, **kwargs):
        """ Actual wrapping

        [한국어]
        실제 래핑이 이뤄지는 내부 함수. 원래 함수를 호출하기 전후로
        entering()/exiting() 로깅을 끼워 넣고 원래 결과를 그대로 반환한다.
        """
        entering(func, *args)
        result = func(*args, **kwargs)
        exiting(func)
        return result
    return call


def entering(func, *args):
    """ Pre function logging

    [한국어]
    함수 실행 직전에 호출되는 로깅 함수. 함수 이름, docstring, 정의된
    줄 번호와 파일, 그리고 첫 번째 인자 값을 디버그 로그로 남긴다.
    인자가 없으면 "No arguments"를 남긴다.
    """
    CybORGLogger.debug("Entered %s", func.__name__)
    CybORGLogger.debug(func.__doc__)
    CybORGLogger.debug(
        "Function at line %d in %s" % (func.__code__.co_firstlineno,
                                       func.__code__.co_filename)
    )

    try:
        CybORGLogger.debug(
            "The argument %s is %s" % (func.__code__.co_varnames[0], *args)
        )
    except IndexError:
        CybORGLogger.debug("No arguments")


def exiting(func):
    """ Post function logging

    [한국어]
    함수 실행 직후에 호출되는 로깅 함수. 함수 이름을 디버그 로그로 남긴다.
    """
    CybORGLogger.debug("Exited  %s", func.__name__)

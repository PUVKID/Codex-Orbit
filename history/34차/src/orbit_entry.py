"""단일 EXE에서 일반 GUI와 내부 GPU 자식 진입을 먼저 분기합니다."""
import sys


def main(arguments=None):
    arguments = sys.argv[1:] if arguments is None else arguments
    # 손상된 내부 요청도 일반 앱으로 떨어져 두 번째 GUI를 만들지 않습니다.
    if any(str(value).startswith('--orbit-gpu-child') for value in arguments):
        if not arguments or arguments[0] != '--orbit-gpu-child': return 64
        try:
            from calendar_gpu_child import main as child_main
            return child_main(arguments[1:])
        except Exception as error:
            if sys.stderr is not None: print('GPU 내부 시작 실패: ' + str(error), file=sys.stderr)
            return 64
    from app import main as app_main
    return app_main()


if __name__ == '__main__':
    raise SystemExit(main())

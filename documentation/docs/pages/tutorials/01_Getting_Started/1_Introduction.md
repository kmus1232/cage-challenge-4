# Installation Instructions (설치 안내)

## Setup (사전 준비)

The following are required software to begin the installation process:

> 설치를 시작하려면 다음 소프트웨어가 필요합니다.

- Git
- Python3 (recommended version 3.10)
- Pip

> - Git
> - Python3 (권장 버전 3.10)
> - Pip

!!! tip "Virtual Environment"
    
    We recommend using a virtual environment running python 3.10 or later. 
    See '[Optional: Create a Virtual Environment](#optional-create-a-virtual-environment)' below' for instructions.

> !!! tip "가상 환경(Virtual Environment)"
>
>     Python 3.10 이상에서 동작하는 가상 환경(virtual environment)을 사용하기를 권장합니다.
>     자세한 방법은 아래 '[Optional: Create a Virtual Environment](#optional-create-a-virtual-environment)' 섹션을 참고하세요.

## Download (내려받기)

Clone the repository to your machine.

> 레포지토리를 사용 중인 컴퓨터로 클론(clone, 복제)합니다.

```
git clone >>>INSERT_URL_HERE<<<
```

## Optional: Create a Virtual Environment (선택 사항: 가상 환경 만들기)

A virtual environment is a self-contained virtual space within which you can download the required software dependencies for a relevant project without risking clashes with others. In this case, it allows your enviroment to be stable, disposable and reproducable. 

> 가상 환경은 그 자체로 독립된 가상 공간으로, 다른 프로젝트와의 충돌 위험 없이 해당 프로젝트에 필요한 소프트웨어 의존성(dependency)을 설치할 수 있게 해줍니다. 이렇게 하면 환경을 안정적이고(stable), 언제든 버릴 수 있으며(disposable), 재현 가능하게(reproducible) 유지할 수 있습니다.

To create a virtual environment, you must first install the `virtualenv` module. 

> 가상 환경을 만들려면 먼저 `virtualenv` 모듈을 설치해야 합니다.

Do so thusly:

> 다음과 같이 설치합니다.

```
pip install --user virtualenv
```

Once downloaded, create a venv using the following command:

> 설치가 끝나면 다음 명령으로 venv(가상 환경)를 생성합니다.

```
python3 -m venv >>>PATH_TO_VENV<<<
```

`>>>PATH_TO_VENV<<<` is the directory you want to store the venv in.

> `>>>PATH_TO_VENV<<<` 는 venv를 저장할 디렉터리(경로)를 의미합니다.

To enable the venv:

> venv를 활성화하려면 다음과 같이 실행합니다.

```
source >>>PATH_TO_VENV<<</bin/activate
```

!!! tip "Done with CybORG?"
    
    Once you're done, you can disable the venv by simply running the command `deactivate`

> !!! tip "CybORG 사용을 마쳤나요?"
>
>     작업이 끝났다면 `deactivate` 명령만 실행하면 venv를 비활성화할 수 있습니다.

## Requirements (의존성 설치)

Install the dependencies (as listed in `Requirements.txt`), ensuring you are in the main directory.

> 메인 디렉터리에 있는지 확인한 뒤, (`Requirements.txt`에 나열된) 의존성을 설치합니다.

```
pip install -r Requirements.txt
```

Locally install CybORG.

> CybORG(Cyber Operations Research Gym)를 로컬에 설치합니다.

!!! warning "Don't run the following command with `sudo`"
    
> !!! warning "다음 명령을 `sudo`로 실행하지 마세요"

```
pip install -e .
```

Install the Tcl/Tk GUI toolkit tkinter:

> Tcl/Tk GUI 툴킷인 tkinter를 설치합니다.

```
sudo apt install python3-tk --assume-yes
```

## Testing your Install (설치 확인)

Run the following tests to check you've installed CybORG correctly.

> CybORG가 올바르게 설치되었는지 확인하려면 다음 테스트를 실행합니다.

```
pytest ./CybORG/Tests/test_cc4
```

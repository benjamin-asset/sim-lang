# Define global args
ARG FUNCTION_DIR="/home/app/"
ARG RUNTIME_VERSION="3.9"
ARG DISTRO_VERSION="3.12"

# 1단계 - 번들 기본 이미지 + 런타임
# 새로운 이미지 복사본을 가져오고 GCC를 설치함
FROM python:${RUNTIME_VERSION}-alpine${DISTRO_VERSION} AS python-alpine
# GCC 설치(Alpine은 musl을 사용하지만 여기에서는 종속성을 GCC와 컴파일하고 연결함)
RUN apk add --no-cache \
    libstdc++

# 2단계 - 함수 및 종속성 빌드
FROM python-alpine AS build-image
# aws-lambda-cpp 빌드 종속성 설치
RUN apk add --no-cache \
    build-base \
    libtool \
    autoconf \
    automake \
    libexecinfo-dev \
    make \
    cmake \
    git \
    curl
# 파이썬 관련 의존성 설치
RUN apk add --no-cache \
  gcc \
  musl-dev \
  python3-dev \
  libffi-dev \
  openssl-dev \
  cargo \
  gfortran \
  build-base \
  wget \
  freetype-dev \
  libpng-dev \
  openblas-dev
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h
# 빌드의 현재 단계에 전역 args 포함
ARG FUNCTION_DIR
ARG RUNTIME_VERSION
# 함수 디렉토리 만들기
RUN mkdir -p ${FUNCTION_DIR}
# 처리자 함수 복사
COPY sim_lang/* ${FUNCTION_DIR}
# 선택 사항 – 함수의 종속성 설치
# Python용 Lambda Runtime Interface Client 설치
RUN python${RUNTIME_VERSION} -m pip install pip -U
RUN python${RUNTIME_VERSION} -m pip install awslambdaric --target ${FUNCTION_DIR}
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python${RUNTIME_VERSION} -
COPY pyproject.toml poetry.lock /
RUN $HOME/.poetry/bin/poetry config virtualenvs.create false && $HOME/.poetry/bin/poetry install
# 3단계 - 최종 런타임 이미지
# Python 이미지의 새로운 복사본 가져오기
FROM python-alpine
# 빌드의 현재 단계에 전역 arg 포함
ARG FUNCTION_DIR
# 작업 디렉토리를 함수 루트 디렉토리로 설정
WORKDIR ${FUNCTION_DIR}
# 빌드된 종속성 복사
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}
# (선택 사항) Lambda Runtime Interface Emulator를 추가하고 보다 간단한 로컬 실행을 위해 ENTRYPOINT에서 스크립트 사용
ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
RUN chmod 755 /usr/bin/aws-lambda-rie
COPY docker/entry.sh /
RUN chmod 755 /entry.sh
ENTRYPOINT [ "/entry.sh" ]

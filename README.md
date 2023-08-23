# django-channels-practice

Django Channels를 활용한 비동기 웹 애플리케이션 연습 레포지토리

## Overview
![ezgif-1-62828656fc](https://github.com/sungbinlee/django-channels-practice/assets/52542229/78db0a1e-20cd-4643-987a-c4f05423c0bc)

채팅 서비스의 핵심은 실시간 메세징

## 서버에서 웹 클라이언트로 메세지를 전달하려면?

### HTTP Polling (실시간 X)

- 서버로 일정주기로 요청/응답 반복(새로고침 연타)
- 구현 간단, 비효율적
- 반복된 HTTP 요청/응답 에서 요청/응답 패킷의 오버헤드가 큼.

### HTTP Long Polling

- 서버에 요청을보내고 응답을 받을때 까지 연결을 유지하며, 응답을 대기
- 연결이 끊어지거나 응답을 받으면 다시 요청
- 메세지가 많을 경우 풀링과 유사

### HTTP Streaming

- 서버에 요청을 보내고, 연결이 유지된 상태에서 데이터를 계속 수신
- 이벤트 목적보다 큰 크기의 응답을 해야할 때 유용
- 클라이언트에서 서버로의 전송 X

### Web Socket (실시간 O)

- 연결이 유지되는 동안, 양방향 통신 지원
- 클라이언트/서버 상호 간에 즉시성이 높은 데이터 전송
- HTTP와 동일한 포트(80/443) 사용
- 장고 채널스에서 지원

## Redis Pub/Sub

서버 단에서 채팅방의 다른 유저에게 메세지를 뿌리는 역할. 유저로의 전달은 웹소켓이 담당.

- 레디스 특정 채널에 구독신청을 하면 Subscriber가 됩니다. 레디스 특정 채널에 메세지를 Publish 하면, 구독 중인 구독자에게 메세지가 전달됩니다.
  - ex: 유튜브 구독
- 레디스의 Pub/Sub는 메세지를 "전달하는" 시스템이기에 메세지를 보관하지 않습니다.
  - 지난 채팅 메세지 조회 필요시 메세지를 DB에 넣고 조회
- 서버 대수를 늘려 Horizontal로 손쉬운 Scale out을 지원

## 메시지 흐름

![제목 없는 다이어그램 drawio (1)](https://github.com/sungbinlee/django-channels-practice/assets/52542229/3fe82112-f638-4d16-b894-e9fe3c727831)

채널스의 Consumer Instance는 레디스의 Pub/Sub과 유저와의 메세지 중개자 역할을 하며각 웹 소켓 연결마다 하나씩 생성합니다.
유저 A -송신-> Consumer Instance -송신-> Redis Pub/Sub -> 채팅방에 있는 다른 유저들의 Consumer Instance를 경유 -> 유저 B/C/D

## 웹 애플리케이션 서버 인터페이스: WSGI와 ASGI 소개

장고는 WSGI / ASGI 모두를 기본에서 잘 지원하며, 원하는 방식으로 구동

- 장고의 일반적인 뷰 처리는 (Django, DRF 등) WSGI 방식이 성능이 더 잘 나올수도 있습니다.

### WSGI

Web Server Gateway Interface

- Synchronous 파이썬 HTTP 웹에 대한 파이썬 표준
- HTTP 요청/응답의 단일 처리만 가능한 방식, 웹소켓 지원 불가

### ASGI

Asynchronous Server Gateway Interface

- WSGI의 정신적 계승자
- HTTP 프로토콜 뿐만 아니라 웹소켓 등의 다양한 프로토콜을 지원할 수 있는 기반을 제공
- WSGI과의 호환성 지원과 더불어 Asynchronous / Synchronous 모두에 대한 파이썬 표준을 제공

## [Channels](https://github.com/django/channels)

- ASGI 기반의 라이브러리로써, HTTP/웹소켓 프로토콜을 손쉽게 처리할 수 있도록 기능 지원
  - 장고 네이티브한 방법으로 웹소켓 지원
- 파이썬 3.7 이상, 장고 2.2 이상을 지원

### 웹소켓 처리에 대한 완벽한 추상화 지원

연결수락/송신/수신/끊기
웹 소켓 처리 시에 특별한 세팅없이도, 모델/세션/쿠키/인증/캐시 템플릿 등의 장고의 모든기능을 사용할수 있습니다. 웹소켓에서 웹페이지와 동일하게 쿠키/세션을 모두 사용할 수 있습니다.

### 손쉬운 프로세스 간의 통신(채널레이어 레디스 백엔드를 활용)

- 코드 몇줄로 유저 A의 채팅 메세지를 다른 유저에게 전달토록(브로드캐스팅) 개발 가능!

### 채널과 그룹

#### 채널

- Consumer Instance 내부에서 생성
- 하나의 연결마다 Consumer 클래스의 Instance가 자동으로 생성되며, 각 Consumer Instance마다 고유한 채널명을 가집니다.
- 그 채널을 통해 Consumer Instance는 채널 레이어와 통신합니다.

#### 그룹

- 여러 Consumer Instance를 묶는 논리적인 묶음.
- 그룹명을 알면, 그 그룹에 속한 모든 Consumer Instances에게 메세지를 보낼 수 있습니다.

### Channels를 구성하는 패키지

- channels: (필수) 장고 통합 레이어
- daphne: (필수) ASGI 서버
  - channels 4.0부터 장고/채널스 개발서버로 사용
  - 실서비스에서는 daphne 명령이나 gunicorn/uvicorn 명령을 사용하여, 장고 서버를 구동
- channels_redis: (옵션) Redis 채널 레이어
  - Channels 구동에 필수는 아니지만, 채팅 서비스에서는 프로세스간 통신이 필요하기에 필요

### Scope

현재 요청의 세부 내역이 담긴 dict
scope은 dict 타입. 채널스 미들웨어에 의해 새로은 key/value가 설정됩니다.

#### 장고

- 장고 기본에서는 HTTP 요청을 처리하는 주체는 View, 함수와 클래스 형태
  View 에서는 HttpRequest 객체를 통해서 유저/세션/쿠키/헤더 등의 현재 요청의 모든 내역을 조회할 수 있습니다.

```python
# 장고 함수기반 뷰
def chatroom_list(request):
    request.user     # 현재 요청의 User 인스턴스
    request.session
    request.COOKIES
    request.headers
    request.GET
    #...

# 장고 클래스 기반 뷰

from django.views.generic import ListView

class ChatRoomListView(ListView):
    def get(self, **kwargs):
        self.request.user     # 현재 요청의 User 인스턴스
        self.request.session
        self.request.COOKIES
        self.request.headers
        self.request.GET
        #...

```

#### 채널스

- 채널스 에서는 HTTP와 웹소켓 요청을 처리하는 주체가 Consumer 클래스, 함수X 클래스로만 구현
  Consumer Instance에서는 self.scope 사전을 통해 현재의 요청의 모든 내역을 조회할 수 있습니다.

```python
from channels.generic.websocket import WebsocketConsumer

class ChatConsumer(websocketConsumer):
    def connect(self):
        self.user = self.scope["user"] # 현재 요청의 User 인스턴스
        self.scope["session"]
        self.scope["cookies"]
        self.scope["headers"]
        self.scope["url_route"]

        if self.user.is_authenticated:
            # ...
            self.user.uesrname
            self.user.email
        room_name = self.scope["url_route"]["kwargs"]["name"]
        # ...
```

### 채널스 구성요소

Consumer 클래스는 채널스에서 요청을 처리하는 주체로서 일관된 처리방법을 제시합니다.

- 채널스는 ASGI application을 층층이 싾는 방식으로 구현 - 래핑 방식으로 동작

## Redis 서버 구동 및 접속

### Redis란?

- 고성능 오픈소스 메모리 Key/Value NoSQL 데이터 베이스
- 주요 사용 사례 : 캐싱, 세션 저장, **Pub/Sub** 랭킹서버 등, 그리고 **Channels의 ChannelsLayer 백엔드**
- 다양한 자료구조를 지원
  - strings, Bitmaps, Hashes, Lists, Sets, Sorted Sets, Geospatial Indexes 등

### Redis 서버 구동 방법

- 외부 서비스를 활용
  - Redis Enterprise Cloud의 Free Plan(무료/유료)
  - 다양한 클라우드 벤더의 Redis as a Service 활용(무료/유료)
- 로컬에 직접 설치
  - 도커 활용
  - os용 배포판 설치(윈도우는 미지원WSL 활용)

## 채널 레이어

채널 레이어를 활용한 프로세스간 통신

- 서로 다른 프로세스 간에 메세지를 전달할 때, 중개자 역할
  - 주로 Consumer Instances에서 메세지를 소비/발행하지만,
  - 장고 뷰/모델, Celery Tasks를 비롯한 모든 장고 영역에서 메세지를 발행할 수 있습니다.
- 활용 예

  - 새로운 모델 인스턴스가 저장되면, 접속 유저에게 알리기(from 모델)
  - 긴 배치작업을 끝내고 나서, 접속 유저에게 알리기

### Channel Layer 백엔드

settings.CHANNEL_LAYERS 설정을 통해 설정

- 인메모리 (초기 개발용): Channels 기본에서 제공

  - 프로세스가 다수인 환경에서는, 각 프로세스 별로 메모리가 격리되어 동작하기에, 프로세스간 통신이 불가능합니다.
  - 단일 프로세스 배포 환경에서는 의미가 있습니다.

- 레디스 (개발 및 실서비스용)
  - 각 프로세스들이 네트워크를 통해 레디스를 공유하기에, 각 프로세스들을 같은 레이어로 동작시킬 수 있습니다.
  - channels_redis 라이브러리를 통해 제공

### 예시

1. 지정 채널명의 Consumer Instance에게 메세지 보내기

- channel_layer.send(채널명, 메세지)
  - 채널명을 알고 있는 장고 어떤 영역에서든 지정 Consumer Instancedㅔ 메세지를 보낼 수 있습니다.
  - 채널명은 랜덤으로 결정되기에, 이를 알고 메세지를 보내는 일은 적습니다.

2. 지정 그룹에 특정 채널을 추가/제거
   Channel Layersd API. 그룹에 추가되면, 그룹 단위로 메세지를 받을 수 있습니다.

- channel_layer.group_add(그룹명, 채널명)

  - 수동으로 지정 그룹에 지정 채널을 추가합니다.
  - 그룹명이 고정되지 않은 경우에 유용

- channel_layer.group_discard(그룹명, 채널명)

  - 수동으로 지정 그룹에서 지정 채널을 제거합니다.
  - group_add를 수행한 Consumer Instance는 제거되기 전에, 필히 group_discard를 수행해야합니다.

- 그룹명이 고정된 경우에는 클래스 변수 groups 리스트를 활용하면, 자동으로 group add/discard를 수행해줍니다.

```python
class LiveblogConsumer(WebsocketConsumer):
  groups = ["liveblog"]

  #...
```

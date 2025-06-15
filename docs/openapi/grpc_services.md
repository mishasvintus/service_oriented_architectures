# gRPC Services Documentation

Данный документ содержит информацию о gRPC сервисах в архитектуре Social Media API.

## Обзор

gRPC сервисы используют Protocol Buffers для определения интерфейсов и обмена данными.
В отличие от REST API, они не имеют OpenAPI документации, но предоставляют строго типизированные интерфейсы.

## Сервисы

### Post Service

- **Протокол**: gRPC
- **Порт**: 50051
- **Proto файл**: `services/post_service/protos/posts.proto`

**Доступные методы:**

#### PostService

- `CreatePost(CreatePostRequest) -> PostResponse`
- `GetPost(GetPostRequest) -> PostResponse`
- `UpdatePost(UpdatePostRequest) -> PostResponse`
- `DeletePost(DeletePostRequest) -> DeletePostResponse`
- `ListPosts(ListPostsRequest) -> ListPostsResponse`
- `ViewPost(ViewPostRequest) -> ViewPostResponse`
- `LikePost(LikePostRequest) -> LikePostResponse`
- `UnlikePost(UnlikePostRequest) -> UnlikePostResponse`
- `CommentPost(CommentPostRequest) -> CommentPostResponse`
- `GetPostComments(GetPostCommentsRequest) -> GetPostCommentsResponse`

### Statistics Service

- **Протокол**: gRPC
- **Порт**: 50053
- **Proto файл**: `services/statistics_service/protos/statistics.proto`

**Доступные методы:**

#### StatisticsService

- `GetPostStats(GetPostStatsRequest) -> GetPostStatsResponse`
- `GetPostViewsDynamics(GetPostDynamicsRequest) -> GetPostDynamicsResponse`
- `GetPostLikesDynamics(GetPostDynamicsRequest) -> GetPostDynamicsResponse`
- `GetPostCommentsDynamics(GetPostDynamicsRequest) -> GetPostDynamicsResponse`
- `GetTopPosts(GetTopPostsRequest) -> GetTopPostsResponse`
- `GetTopUsers(GetTopUsersRequest) -> GetTopUsersResponse`

## Подключение к gRPC сервисам

Для подключения к gRPC сервисам используйте соответствующие клиентские библиотеки:

```python
import grpc
from generated_pb2 import *
from generated_pb2_grpc import *

# Создание канала
channel = grpc.insecure_channel('localhost:PORT')
stub = ServiceStub(channel)

# Вызов метода
response = stub.Method(Request())
```

## Генерация клиентского кода

Для генерации клиентского кода из proto файлов используйте:

```bash
python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. your_service.proto
```

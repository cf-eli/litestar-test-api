from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict

from litestar import Litestar, Request, post, get
from litestar.datastructures import UploadFile
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.config.cors import CORSConfig

# --- Pydantic Model Definition ---
# This model is used by endpoints that expect a JSON body.
class ExampleModel(BaseModel):
    example_int: int
    example_str: str

class FooModel(BaseModel):
    foo: str
    bar: int
# --- Route Handlers ---

@get(path="/api/v1/path_param/{random_int:int}", tags=["Path"])
async def path_param(random_int: int) -> Dict[str, Any]:
    return {"foo": "bar", "custom_int": random_int}


@post(path="/api/v1/path_and_body/{path_int:int}", tags=["Path", "Body"])
async def path_and_body(path_int: int, data: FooModel) -> Dict[str, Any]:
    return {"foo": "bar", "path_int": path_int, **data.model_dump()}


@get(path="/api/v1/list_model", tags=["List"])
async def list_model() -> List[Dict[str, str]]:
    return [{"foo_key": "foo"}, {"foo_key": "bar"}]


@post(path="/api/v1/body", tags=["Body"])
async def body(data: ExampleModel) -> Dict[str, Any]:
    # Litestar automatically maps the JSON body to the pydantic model 'data'
    return {"query_int": data.example_int, "query_str": data.example_str}


@get(path="/api/v1/query", tags=["Query"])
async def query(query_int: int, query_str: str) -> Dict[str, Any]:
    # Query parameters are automatically extracted from the function signature
    return {"query_int": query_int, "query_str": query_str}


@post(path="/api/v1/query_and_body", tags=["Query", "Body"])
async def query_and_body(query_int: int, query_str: str, data: ExampleModel) -> Dict[str, Any]:
    return {"query_int": query_int, "query_str": query_str, **data.model_dump()}


@post(path="/api/v1/query_and_body_path/{path:int}", tags=["Query", "Body", "Path"])
async def query_and_body_path(
    path: int, query_int: int, query_str: str, data: FooModel
) -> Dict[str, Any]:
    print(data)
    return {
        "query_int": query_int,
        "query_str": query_str,
        "path": path,
        **data.model_dump(),
    }

class LoginForm(BaseModel):
    username: str
    password: str


@post("/api/v1/form_data", tags=["Form"])
async def form_data(
    # The signature now accepts a single 'data' parameter of type LoginForm
    data: LoginForm = Body(media_type=RequestEncodingType.URL_ENCODED)
) -> Dict[str, Any]:
    """
    Accepts URL-encoded form data and maps it to a LoginForm model.
    """
    # Access the fields via the model attributes
    return {"foo": "bar", "username": data.username, "password": data.password}


class FileUploadModel(BaseModel):
    """
    Model to handle file uploads.
    """
    file: UploadFile
    model_config = ConfigDict(arbitrary_types_allowed=True)



@post(path="/api/v1/upload_file", tags=["Form", "File"])
async def upload_file(
    data: FileUploadModel = Body(media_type=RequestEncodingType.MULTI_PART),
) -> Dict[str, Any]:
    return {"filename": data.file.filename, "file_content_type": data.file.content_type}


class FormUploadModel(BaseModel):
    username: str
    password: str
    file: UploadFile

    model_config = ConfigDict(arbitrary_types_allowed=True)


@post(path="/api/v1/form_and_upload_file", tags=["Form", "File"])
async def form_and_upload_file(
    data: FormUploadModel = Body(media_type=RequestEncodingType.MULTI_PART),
    # username: str = Body(media_type=RequestEncodingType.MULTI_PART),
    # password: str = Body(media_type=RequestEncodingType.MULTI_PART),
    # file: UploadFile = Body(media_type=RequestEncodingType.MULTI_PART),
) -> Dict[str, Any]:
    return {
        "username": data.username,
        "pwd": data.password,
        "filename": data.file.filename,
        "content_type": data.file.content_type,
    }


@get(path="/api/v1/check_dependency_header", tags=["Dependency"])
async def check_dependency_header_get(request: Request) -> Dict[str, Any]:
    return {"header": request.headers.get("x-api-key"), "foo": "bar"}


@post(path="/api/v1/check_dependency_header", tags=["Dependency"])
async def check_dependency_header_post(
    username: str = Body(media_type=RequestEncodingType.URL_ENCODED),
    password: str = Body(media_type=RequestEncodingType.URL_ENCODED),
) -> Dict[str, Any]:
    return {"username": username, "password": password}



from litestar.openapi.spec import Components, SecurityScheme, OAuthFlows, OAuthFlow
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import SwaggerRenderPlugin

components = Components(
    security_schemes={
        "bearerAuth": SecurityScheme(
            type="http",
            scheme="bearer",
            bearer_format="JWT",
            description="Paste your JWT here"
        )
    }
)

openapi_config = OpenAPIConfig(
    title="API Gateway",
    version="1.0.0",
    path="/docs",
    render_plugins=[
        SwaggerRenderPlugin()
    ],
    components=components,
    security=[{"bearerAuth": []}]
)

cors_config = CORSConfig(
    allow_origins=["*"],  # Adjust as needed
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=False

)


def create_app() -> Litestar:
    """
    Create and return the Litestar application instance.
    This function is used to initialize the app in the ASGI server.
    """
 
# --- Litestar Application Instance ---
    app = Litestar(
        route_handlers=[
            path_param,
            path_and_body,
            list_model,
            body,
            query,
            query_and_body,
            query_and_body_path,
            form_data,
            upload_file,
            form_and_upload_file,
            check_dependency_header_get,
            check_dependency_header_post,
        ],
        openapi_config=openapi_config,
        cors_config=cors_config,

        # title="Microservice #1 (Litestar)",
    )
    return app
from models.db import SessionLocal
from models.projects import Project
from models.users import User
from routes.common import templates

from typing import Annotated
from urllib.parse import quote_plus

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def homepage(request: Request, error: str = "", username: str = "") -> HTMLResponse:
    with SessionLocal() as db:
        projects = db.query(Project).order_by(Project.name).all()

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "request": request,
            "error": error,
            "username": username,
            "projects": projects,
        },
    )


@router.post("/login")
def login(
        request: Request,
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
) -> RedirectResponse:
    with SessionLocal() as db:
        user = db.query(User).filter(User.username == username).first()
        if not user or user.password != password:
            encoded_username = quote_plus(username)
            return RedirectResponse(
                url=f"/?error=Invalid+username+or+password&username={encoded_username}",
                status_code=303,
            )

        if user.role == "unvalidated":
            encoded_username = quote_plus(username)
            return RedirectResponse(
                url=f"/?error=Account+pending+approval&username={encoded_username}",
                status_code=303,
            )

        request.session["user_id"] = user.id

    return RedirectResponse(url="/dashboard", status_code=303)


@router.post("/create-account")
def create_account(
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
        project_action: Annotated[str, Form()],
        project_id: Annotated[str | None, Form()] = None,
        project_name: Annotated[str | None, Form()] = None,
) -> RedirectResponse:
    with SessionLocal() as db:
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            encoded_username = quote_plus(username)
            return RedirectResponse(
                url=f"/?error=User+already+exists&username={encoded_username}",
                status_code=303,
            )

        role = "unvalidated"
        if project_action == "create":
            clean_project_name = (project_name or "").strip()
            if not clean_project_name:
                encoded_username = quote_plus(username)
                return RedirectResponse(
                    url=f"/?error=Project+name+is+required&username={encoded_username}",
                    status_code=303,
                )

            existing_project = db.query(Project).filter(Project.name == clean_project_name).first()
            if existing_project:
                encoded_username = quote_plus(username)
                return RedirectResponse(
                    url=f"/?error=Project+already+exists&username={encoded_username}",
                    status_code=303,
                )

            project = Project(name=clean_project_name)
            db.add(project)
            db.flush()
            selected_project_id = project.id
            role = "admin"
        elif project_action == "join":
            if not project_id:
                encoded_username = quote_plus(username)
                return RedirectResponse(
                    url=f"/?error=Please+select+a+project&username={encoded_username}",
                    status_code=303,
                )

            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                encoded_username = quote_plus(username)
                return RedirectResponse(
                    url=f"/?error=Project+not+found&username={encoded_username}",
                    status_code=303,
                )
            selected_project_id = project.id
        else:
            encoded_username = quote_plus(username)
            return RedirectResponse(
                url=f"/?error=Invalid+project+action&username={encoded_username}",
                status_code=303,
            )

        user = User(
            username=username.strip(),
            password=password,
            role=role,
            project_id=selected_project_id,
        )
        db.add(user)
        db.commit()

    return RedirectResponse(url="/?error=Account+created.+Please+log+in", status_code=303)


@router.post("/logout")
def logout(request: Request) -> RedirectResponse:
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)

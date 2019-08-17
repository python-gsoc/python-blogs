import json
from collections.abc import Sequence

from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.template import Template

from github import Github


def build_send_mail_json(
    send_to, template: str, subject: str, template_data: dict = None
):
    if not isinstance(send_to, Sequence) and not isinstance(send_to, str):
        raise TypeError(
            "send_to must be a sequence of email addresses "
            "or one email address as str!"
            )
    return json.dumps(locals())


def build_send_reminder_json(
    send_to, object_pk, template: str, subject: str, template_data: dict = None
):
    if not isinstance(send_to, Sequence) and not isinstance(send_to, str):
        raise TypeError(
            "send_to must be a sequence of email addresses "
            "or one email address as str!"
            )
    return json.dumps(locals())


def send_mail(send_to, subject, template, context={}):
    try:
        template = get_template(f"email/{template}")
    except TemplateDoesNotExist:
        template = Template(template)

    content = template.render(context)
    if isinstance(send_to, str):
        send_to = [send_to]

    send_email = EmailMessage(
        body=content,
        subject=settings.EMAIL_SUBJECT_PREFIX + subject,
        from_email=settings.SERVER_EMAIL,
        reply_to=settings.REPLY_EMAIL,
        to=send_to,
        )
    send_email.content_subtype = "html"
    send_email.send()


def render_site_template(template, context):
    try:
        template = get_template(f"site/{template}")
    except TemplateDoesNotExist:
        template = Template(template)

    return template.render(context)


def create_branch(target_branch, source_branch="master"):
    g = Github(settings.GITHUB_ACCESS_TOKEN)
    repo = g.get_repo(settings.STATIC_SITE_REPO)
    sb = repo.get_branch(source_branch)
    repo.create_git_ref(ref=f"refs/heads/{target_branch}", sha=sb.commit.sha)
    return target_branch


def create_pull_request(source_branch, target_branch="master"):
    g = Github(settings.GITHUB_ACCESS_TOKEN)
    repo = g.get_repo(settings.STATIC_SITE_REPO)
    repo.create_pull(
        title="Site Template Update", body="", base=target_branch, head=source_branch
        )


def push_site_template(file_path, content, branch):
    content = content.encode()
    g = Github(settings.GITHUB_ACCESS_TOKEN)
    repo = g.get_repo(settings.STATIC_SITE_REPO)
    f = repo.get_contents(file_path)
    repo.update_file(f.path, f"Update {file_path}", content, f.sha, branch=branch)


def push_images(file_path, content, branch):
    g = Github(settings.GITHUB_ACCESS_TOKEN)
    repo = g.get_repo(settings.STATIC_SITE_REPO)
    repo.create_file(file_path, f"Add {file_path} logo", content, branch=branch)


def is_year(file_name):
    try:
        year = int(file_name)
        if year >= 2000 and year <= 2100:
            return True
        return False
    except Exception as e:
        return False


def get_files(
    repo, except_files=["CNAME", "LICENSE.md", "README.md", "favicon.ico", "robots.txt"]
):
    contents = repo.get_contents("")
    files = []
    while contents:
        file_content = contents.pop(0)
        if not (file_content.path in except_files or is_year(file_content.path)):
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                files.append(file_content)
    return files


def update_robots_file(repo, current_year):
    c = repo.get_contents("robots.txt")
    new_content = c.decoded_content.strip() + f"\nDisallow: /{current_year}/\n".encode()
    repo.update_file(c.path, "Update robots.txt", new_content, c.sha)


def archive_current_gsoc_files(current_year):
    # g = Github(settings.GITHUB_ACCESS_TOKEN)
    g = Github('sounak98', 'Soun@k1998_1965')
    repo = g.get_repo(settings.STATIC_SITE_REPO)
    files = get_files(repo)
    update_robots_file(repo, current_year)
    for file in files:
        decoded_content = file.decoded_content
        if file.path.split('.')[-1] == "html":
            decoded_content = decoded_content.replace(b"</body>", b"""
                <style>
                .modalDialog {
                    position: fixed;
                    font-family: Arial, Helvetica, sans-serif;
                    top: 0;
                    right: 0;
                    bottom: 0;
                    left: 0;
                    background: rgba(0, 0, 0, 0.8);
                    z-index: 99999;
                    opacity: 0;
                    -webkit-transition: opacity 400ms ease-in;
                    -moz-transition: opacity 400ms ease-in;
                    transition: opacity 400ms ease-in;
                    pointer-events: none;
                }
                .modalDialog:target {
                    opacity: 1;
                    pointer-events: auto;
                }
                .modalDialog > div {
                    width: 400px;
                    position: relative;
                    margin: 10% auto;
                    padding: 5px 20px 13px 20px;
                    border-radius: 10px;
                    background: #fff;
                    background: -moz-linear-gradient(#fff, #999);
                    background: -webkit-linear-gradient(#fff, #999);
                    background: -o-linear-gradient(#fff, #999);
                }
                .close {
                    background: #606061;
                    color: #ffffff;
                    line-height: 25px;
                    position: absolute;
                    right: -12px;
                    text-align: center;
                    top: -10px;
                    width: 24px;
                    text-decoration: none;
                    font-weight: bold;
                    -webkit-border-radius: 12px;
                    -moz-border-radius: 12px;
                    border-radius: 12px;
                    -moz-box-shadow: 1px 1px 3px #000;
                    -webkit-box-shadow: 1px 1px 3px #000;
                    box-shadow: 1px 1px 3px #000;
                }
                .close:hover {
                    background: #00d9ff;
                }
                </style>

                <div id="openModal" class="modalDialog">
                <div>
                    <a href="#close" title="Close" class="close">X</a>
                    <h2>Archived</h2>
                    <p>
                    This site has been archived, go to
                    <a target="_blank" href="https://python-gsoc.org/">this link</a> to find
                    more about the latest GSoC program.
                    </p>
                </div>
                </div>

                <script>
                let tokens = String(window.location).split("#");
                if (
                    tokens.length === 1 &&
                    tokens[1] !== "openModal" &&
                    tokens[1] !== "close"
                ) {
                    window.location = window.location + "#openModal";
                }
                </script>
                </body>
            """)
        print(decoded_content)
        try:
            repo.create_file(
                f"{current_year}/{file.path}",
                f"Archive GSoC {current_year} files",
                decoded_content,
                )
        except Exception as e:
            repo.update_file(
                f"{current_year}/{file.path}",
                f"Archive GSoC {current_year} files",
                file.content,
                decoded_content,
                )

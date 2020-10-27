from fastapi import FastAPI, WebSocket, Request, File, Form, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware



import yaml
import ast
from coolname import generate_slug
from datetime import date
from pathlib import Path
from bs4 import BeautifulSoup
from slugify import slugify
#from routers.fastAPI_socialauth import fastAPI_socialauth

app = FastAPI()
#app.include_router(fastAPI_socialauth.router)
#app.add_middleware(HTTPSRedirectMiddleware)

app_path = Path.cwd()
static_path = app_path / "app"/ "site" / "assets"
print(static_path)
app.mount("/assets", StaticFiles(directory=static_path), name="assets")
templates = Jinja2Templates(directory="app/templates")

site_metadata = app_path / "app"/ "site" / "site.yaml"
meta = yaml.load(site_metadata.read_text(), Loader=yaml.FullLoader)
meta["exhibits"] = []

origins = ["{}".format(meta['url']), "http://localhost:8000/"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# read the essays and exhibits directorys, add metadata
def get_essays(meta):
    meta["essays"] = []
    if not (app_path / "app" / "site" / "essay").exists():
        (app_path / "app" / "site" / "essay").mkdir()
    essays = list((app_path / "app" / "site" / "essay").iterdir())
    if essays:
        for essay in essays:
            html = essay.read_bytes()
            soup = BeautifulSoup(html, features="html.parser")

            the = {}
            the["filename"] = essay.name
            the["title"] = soup.find("meta", attrs={"name": "title"}).attrs["content"]
            the["slug"] = soup.find("meta", attrs={"name": "slug"}).attrs["content"]
            the["author"] = soup.find("meta", attrs={"name": "author"}).attrs["content"]
            the["date"] = soup.find("meta", attrs={"name": "date"}).attrs["content"]
            meta["essays"].append(the)
    return essays

def get_exhibits(meta):
    meta["exhibits"] = []
    if not (app_path / "app" / "site" / "exhibit").exists():
        (app_path / "app" / "site" / "exhibit").mkdir()
    exhibits = list((app_path / "app" / "site" / "exhibit").iterdir())
    if exhibits:
        for exhibit in exhibits:
            html = exhibit.read_bytes()
            soup = BeautifulSoup(html, features="html.parser")

            the = {}
            the["filename"] = exhibit.name
            the["title"] = soup.find("meta", attrs={"name": "title"}).attrs["content"]
            the["slug"] = soup.find("meta", attrs={"name": "slug"}).attrs["content"]
            the["author"] = soup.find("meta", attrs={"name": "author"}).attrs["content"]
            the["date"] = soup.find("meta", attrs={"name": "date"}).attrs["content"]
            the["card_image"] = soup.find("meta", attrs={"name": "card_image"}).attrs["content"]
            meta["exhibits"].append(the)
    return exhibits



if meta["dev"] == False:
    essays = get_essays(meta)

    # write index.html to file
    # TODO links to essays incorrect
    # TODO link to essays page incorrect
    path = app_path / "site" / "index.html"
    page = templates.TemplateResponse(
        "index.html", {"request": Request, "meta": meta}
    ).body
    path.write_bytes(page)

    # write about page
    path = app_path / "app" / "site" / "about.html"
    page = templates.TemplateResponse(
        "about.html", {"request": Request, "meta": meta}
    ).body
    path.write_bytes(page)

    # write essays page
    path = app_path / "app" / "site" / "essays.html"
    page = templates.TemplateResponse(
        "essays.html", {"request": Request, "meta": meta}
    ).body
    path.write_bytes(page)

    # write exhibits page

    # fetch all images and save to site/img
    # update img src paths in essays + '../'

if (app_path / "app" / "site" / "exhibit").exists():
    exhibits = list((app_path / "app" / "site" / "exhibit").iterdir())
    meta["exhibits"] = len(exhibits)
else:
    (app_path / "app" / "site" / "exhibit").mkdir()
    meta["exhibits"] = []


@app.get("/")
async def index(request: Request):
    essays = get_essays(meta)
    exhibits = get_exhibits(meta)
    the = {}
    # When there is a GET request with parameters
    if request.query_params:
        if "new_essay" in request.query_params:
            new_essay = request.query_params["new_essay"]
            slug = slugify(new_essay)
            # Check that new title is unique
            if not essays:  # When no essays exist
                unique = []
            else:
                unique = [e for e in meta["essays"] if e["slug"] == slug]

            if len(unique) == 0:

                path = app_path / "app" / "site" / "essay" / (slug + ".html")
                if not path.exists():
                    # Create a new html file from essay template, set title from form
                    path.touch()
                    with path.open("w") as f:
                        row = {}
                        row["filename"] = path.name

                        page = templates.TemplateResponse(
                            "essay.html", {"request": Request, "meta": meta}
                        ).body
                        soup = BeautifulSoup(page, features="html.parser")

                        # change hrefs to load when static
                        for a in soup.find_all(href=True):
                            if a["href"].startswith("assets"):
                                a["href"] = a["href"].replace("assets", "../assets")
                        for s in soup.find_all("script"):
                            try:
                                if s["src"].startswith("assets"):
                                    s["src"] = s["src"].replace("assets", "../assets")
                            except Exception as e:
                                print(e)

                        metatag = soup.new_tag("meta")
                        metatag.attrs["name"] = "title"
                        metatag.attrs["content"] = new_essay
                        soup.head.append(metatag)
                        row["filename"] = new_essay

                        metatag = soup.new_tag("meta")
                        metatag.attrs["name"] = "slug"
                        metatag.attrs["content"] = slug
                        soup.head.append(metatag)
                        row["slug"] = slug

                        metatag = soup.new_tag("meta")
                        metatag.attrs["name"] = "author"
                        metatag.attrs["content"] = "by ..."
                        soup.head.append(metatag)
                        row["author"] = "by ..."

                        metatag = soup.new_tag("meta")
                        metatag.attrs["name"] = "date"
                        metatag.attrs["content"] = date.today().strftime("%B %d, %Y")
                        soup.head.append(metatag)
                        row["date"] = date.today().strftime("%B %d, %Y")

                        meta["essays"].append(row)

                        f.write(str(soup))

                    html = path.read_bytes()
                    soup = BeautifulSoup(html, features="html.parser")

                    the = {}
                    the["title"] = soup.find("meta", attrs={"name": "title"}).attrs[
                        "content"
                    ]
                    the["slug"] = soup.find("meta", attrs={"name": "slug"}).attrs[
                        "content"
                    ]
                    the["author"] = soup.find("meta", attrs={"name": "author"}).attrs[
                        "content"
                    ]
                    the["date"] = soup.find("meta", attrs={"name": "date"}).attrs[
                        "content"
                    ]
                    text = "".join(
                        [e for e in soup.find("div", {"id": "text"}).contents]
                    )
                    if text == "":
                        text = "This essay..."
                    the["text"] = text

                    return templates.TemplateResponse(
                        "edit_essay.html",
                        {"request": request, "slug": slug, "meta": meta, "the": the},
                    )

                else:
                    return templates.TemplateResponse(
                        "edit_essay.html",
                        {"request": request, "slug": slug, "meta": meta, "the": the},
                    )

        # EDIT ESSAY
        # Note that changes are handled by websocket_endpoint below
        elif "edit_essay" in request.query_params:
            edit_essay = request.query_params["edit_essay"]
            slug = slugify(edit_essay)
            path = app_path / "app" / "site" / "essay" / (slug + ".html")
            if not path.exists():
                pass  # TODO add 404 error

            else:
                html = path.read_bytes()
                soup = BeautifulSoup(html, features="html.parser")

                the = {}
                the["title"] = soup.find("meta", attrs={"name": "title"}).attrs[
                    "content"
                ]
                the["slug"] = soup.find("meta", attrs={"name": "slug"}).attrs["content"]
                the["author"] = soup.find("meta", attrs={"name": "author"}).attrs[
                    "content"
                ]
                the["date"] = soup.find("meta", attrs={"name": "date"}).attrs["content"]
                the["text"] = "".join(
                    str(item) for item in soup.find("div", {"id": "text"}).contents
                )

                return templates.TemplateResponse(
                    "edit_essay.html", {"request": request, "the": the, "meta": meta}
                )

        # NEW EXHIBIT
        if "new_exhibit" in request.query_params:
            new_exhibit = request.query_params["new_exhibit"]
            slug = slugify(new_exhibit)
            # Check that new title is unique
            if not exhibits:  # When no essays exist
                unique = []
            else:
                unique = [e for e in meta["exhibits"] if e["slug"] == slug]

            if len(unique) == 0:

                path = app_path / "app" / "site" / "exhibit" / (slug + ".html")
                if not path.exists():
                    # Create a new html file from essay template, set title from form
                    path.touch()
                    with path.open("w") as f:
                        row = {}
                        row["filename"] = path.name

                        page = templates.TemplateResponse(
                            "exhibit.html", {"request": Request, "meta": meta}
                        ).body
                        soup = BeautifulSoup(page, features="html.parser")

                        # change hrefs to load when static
                        for a in soup.find_all(href=True):
                            if a["href"].startswith("assets"):
                                a["href"] = a["href"].replace("assets", "../assets")
                        for s in soup.find_all("script"):
                            try:
                                if s["src"].startswith("assets"):
                                    s["src"] = s["src"].replace("assets", "../assets")
                            except Exception as e:
                                print(e)

                        # add title
                        metatag = soup.new_tag("meta")
                        metatag.attrs["name"] = "title"
                        metatag.attrs["content"] = new_exhibit
                        soup.head.append(metatag)
                        row["filename"] = new_exhibit

                        # add title
                        metatag = soup.new_tag("meta")
                        metatag.attrs["name"] = "slug"
                        metatag.attrs["content"] = slug
                        soup.head.append(metatag)
                        row["slug"] = slug

                        # add author
                        metatag = soup.new_tag("meta")
                        metatag.attrs["name"] = "author"
                        metatag.attrs["content"] = "by ..."
                        soup.head.append(metatag)
                        row["author"] = "by ..."

                        # add card_image url
                        metatag = soup.new_tag("meta")
                        metatag.attrs["name"] = "card_image"
                        metatag.attrs["content"] = "assets/img/nature/image5.jpg"
                        soup.head.append(metatag)
                        row["card_image"] = "assets/img/nature/image5.jpg"

                        # add date created
                        metatag = soup.new_tag("meta")
                        metatag.attrs["name"] = "date"
                        metatag.attrs["content"] = date.today().strftime("%B %d, %Y")
                        soup.head.append(metatag)
                        row["date"] = date.today().strftime("%B %d, %Y")

                        # add items array
                        metatag = soup.new_tag("meta")
                        metatag.attrs["name"] = "items"
                        metatag.attrs["content"] = ""
                        soup.head.append(metatag)

                        

                        meta["exhibits"].append(row)

                        f.write(str(soup))

                    html = path.read_bytes()
                    soup = BeautifulSoup(html, features="html.parser")

                    the = {}
                    #TODO can this be shortened with find_all "meta" and just read all fields in the file?
                    the["title"] = soup.find("meta", attrs={"name": "title"}).attrs[
                        "content"
                    ]
                    the["slug"] = soup.find("meta", attrs={"name": "slug"}).attrs[
                        "content"
                    ]
                    the["author"] = soup.find("meta", attrs={"name": "author"}).attrs[
                        "content"
                    ]
                    the["date"] = soup.find("meta", attrs={"name": "date"}).attrs[
                        "content"
                    ]
                    the["text"] = "".join(
                        str(item) for item in soup.find("div", {"id": "text"}).contents
                    )
                    
                    # populate the mock items and filters 
                    grid = soup.find("div", attrs={"id":"grid"})
                    the["items_"] = grid.find_all('figure')
                    
                    all_filters = []
                    for item_ in the["items_"]:
                        filters = item_.attrs['data-groups'] 
                        filters = ast.literal_eval(filters) 
                        for filter in filters:
                            if filter not in all_filters:
                                all_filters.append(filter)
                   
                    the["filters"]  = all_filters
                    
                    return templates.TemplateResponse(
                        "edit_exhibit.html",
                        {"request": request, "slug": slug, "meta": meta, "the": the},
                    )

                else:
                    return templates.TemplateResponse(
                        "edit_exhibit.html",
                        {"request": request, "slug": slug, "meta": meta, "the": the},
                    )
        
        # EDIT EXHIBIT
        # Note that changes are handled by websocket_endpoint below
        elif "edit_exhibit" in request.query_params:
            edit_exhibit = request.query_params["edit_exhibit"]
            slug = slugify(edit_exhibit)
            path = app_path / "app" / "site" / "exhibit" / (slug + ".html")
            if not path.exists():
                pass  # TODO add 404 error

            else:
                html = path.read_bytes()
                soup = BeautifulSoup(html, features="html.parser")

                the = {}
                the["title"] = soup.find("meta", attrs={"name": "title"}).attrs[
                    "content"
                ]
                the["slug"] = soup.find("meta", attrs={"name": "slug"}).attrs["content"]
                the["author"] = soup.find("meta", attrs={"name": "author"}).attrs[
                    "content"
                ]
                the["date"] = soup.find("meta", attrs={"name": "date"}).attrs["content"]
                the["text"] = "".join(
                    str(item) for item in soup.find("div", {"id": "text"}).contents
                )

                # populate the mock items and filters 
                grid = soup.find("div", attrs={"id":"grid"})
                the["items_"] = grid.find_all('figure')
                
                all_filters = []
                for item_ in the["items_"]:
                    filters = item_.attrs['data-groups'] 
                    filters = ast.literal_eval(filters) 
                    for filter in filters:
                        if filter not in all_filters:
                            all_filters.append(filter)
                   
                the["filters"]  = all_filters
                print(the["filters"])
                return templates.TemplateResponse(
                    "edit_exhibit.html", {"request": request, "the": the, "meta": meta}
                )
    
       
            

    context = {}
    context["meta"] = meta
    context["request"] = request
    meta['message'] = None

    return templates.TemplateResponse("index.html", context)


@app.get("/about")
def about(request: Request):
    context = {}
    context["meta"] = meta
    context["request"] = request
    return templates.TemplateResponse("about.html", context)


@app.get("/essays")
def about(request: Request):
    essays = get_essays(meta)
    return templates.TemplateResponse("essays.html", {"request": request, "meta": meta})


@app.get("/essay/{slug}")
def essay(request: Request, slug: str):
    essay = [e for e in meta["essays"] if e["slug"] == slug]
    assert len(essay) == 1
    html = (app_path / "site" / "essay" / essay[0]["filename"]).read_bytes()
    return HTMLResponse(html)

@app.get("/delete_essay/{slug}")
async def edit_essay(request: Request, slug: str):
    context = {}
    context["meta"] = meta
    context["request"] = request

    path = app_path / "app" / "site" / "essay" / (slug + ".html")
    try:
        path.unlink()
        essay = [e['title'] for e in meta["essays"] if e["slug"] == slug]
        meta["message"] = f"Deleted: {essay[0]}"
    except FileNotFoundError:
        meta["message"] = "File not found"

    return RedirectResponse("/")

@app.get("/delete_exhibit/{slug}")
async def edit_essay(request: Request, slug: str):
    context = {}
    context["meta"] = meta
    context["request"] = request

    path = app_path / "app" / "site" / "exhibit" / (slug + ".html")
    try:
        path.unlink()
        essay = [e['title'] for e in meta["exhibits"] if e["slug"] == slug]
        meta["message"] = f"Deleted: {essay[0]}"
    except FileNotFoundError:
        meta["message"] = "File not found"

    return RedirectResponse("/")

@app.get("add_item/{exhibit}")
async def add_item(exhibit:str, title: str = Form('title')):
    #add item file
    #reload page at same location
    pass

@app.post("create_item/{exhibit}")
async def add_item(exhibit:str, title: str = Form('title')):
    #add item file
    #reload page at same location
    print(exhibit, title)

@app.post("/item_images")
async def create_upload_file(filename: str = Form("filename"), file: UploadFile = Form("file")):
    path = app_path / "app" / "site" / "assets" / "upload" / f"{filename}"
    path.write_bytes(file.file.read())
    # url = f"https://{meta.url}/images/model.png"
    return {
        f"assets/upload/{filename}"
    }

@app.post("/images")
async def create_upload_file(upload: bytes = File("upload")):
    name = generate_slug()
    path = app_path / "app" / "site" / "assets" / "upload" / f"{name}.jpeg"
    path.write_bytes(upload)
    # url = f"https://{meta.url}/images/model.png"
    return {
        "url": f"assets/upload/{name}.jpeg",
    }

# TODO add custom upload adapter to send filenames
# https://ckeditor.com/docs/ckeditor5/latest/framework/guides/deep-dive/upload-adapter.html#the-anatomy-of-the-adapter

# write updates to essay to file https://fastapi.tiangolo.com/advanced/websockets/
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        print('is websocket')
        data = await websocket.receive_text()
        keys = ["type","slug", "title", "author", "text","grid"]
        data = dict(zip(keys, data.split("💾🥞")[1:]))
        print(data)
        slug = data["slug"]
        if data['type'] == 'essay':
            path = app_path / "app" / "site" / "essay" / (slug + ".html")
        else:
            path = app_path / "app" / "site" / "exhibit" / (slug + ".html")
        page = path.read_bytes()
        soup = BeautifulSoup(page, features="html.parser")

        # Update the value in <meta name="title">
        new_title = data["title"]
        meta_title = soup.find("meta", attrs={"name": "title"})
        meta_title["content"] = new_title

        # Update the value in <div id="title"></div>
        div_title = soup.find("div", attrs={"id": "title"})
        div_title.clear()
        new_tag = soup.new_tag("h4")
        new_tag.string = new_title
        div_title.append(new_tag)

        # Update the value in <meta name="author">
        new_author = data["author"]
        meta_author = soup.find("meta", attrs={"name": "author"})
        meta_author["content"] = new_author

        # Update the value in <div id="author"></div>
        div_author = soup.find("div", attrs={"id": "author"})
        div_author.clear()
        new_tag = soup.new_tag("p")
        new_tag.string = new_author
        div_author.append(new_tag)

        # Update the value in <div id="text"></div>
        new_text = data["text"]
        new_soup = BeautifulSoup(new_text, features="html.parser")
        div_text = soup.find("div", attrs={"id": "text"})
        div_text.clear()
        div_text.append(new_soup)

        if data['grid'] != 'none':
            new_grid = data["grid"]
            new_soup = BeautifulSoup(new_grid, features="html.parser")
            div_grid = soup.find("div", attrs={"id": "grid"})
            div_grid.clear()
            div_grid.append(new_soup)
        with path.open("w") as f:
            f.write(str(soup))


@app.get("/exhibits")
def read_item(request: Request):
    context = {}
    context["meta"] = meta
    context["request"] = request
    return templates.TemplateResponse("exhibits.html", context)


@app.get("/essay_html/{filename}")
def read_item(request: Request, filename:str):
    filename = filename + ".html"
    code = (app_path / "app" / "site" / "essay" / filename).read_text()
    context = {}
    context["code"] = code
    context["meta"] = meta
    context["request"] = request
    return templates.TemplateResponse("essay_html.html", context)

@app.post("/change_essay_html")
async def change_essay_code(request: Request):
    data = await request.json()
    code = data["code"]
    filename = data["filename"] + '.html'
    path = (app_path / "app" / "site" / "essay" / filename)
    if path.exists():
        path.write_text(code)
    else:
        return {'error':'file does not exist'}

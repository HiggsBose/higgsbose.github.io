# Zelun Pan · Personal homepage

采用米白、朱红、墨黑和几何构图的个人学术主页。页面为静态 HTML，兼容 GitHub Pages；本地及 CI 都用 Python 3.12 构建，无需 Ruby 或 Node.js。

## 本地预览

已创建环境时，在仓库目录打开 Anaconda Prompt / 支持 conda 的终端：

```powershell
conda activate personal_page
python scripts/site.py serve
```

打开 <http://127.0.0.1:4000>。按 `Ctrl+C` 停止。端口被占用时加 `--port 4001`。

如果终端尚未配置 `conda activate`，可以直接运行：

```powershell
conda run --no-capture-output -n personal_page python scripts/site.py serve
```

新电脑首次安装：

```powershell
conda env create -f environment.yml
conda activate personal_page
```

`serve` 启动前自动构建。修改源文件后，在另一终端重新执行 `python scripts/site.py build`，然后刷新浏览器。预览不依赖外部字体、CDN 或在线脚本。

## 页面与维护

| 页面 | 地址 | 内容来源 |
| --- | --- | --- |
| About | `/` | `content/about.md`、`content/background.json`、`content/profile.json`、`templates/page.html` |
| News | `/news/` | `content/news.md` |
| Publications | `/publications/` | `content/publications.md` |
| Talks | `/talks/` | `content/talks.md` |
| Projects | `/projects/` | `content/projects.md` |
| CV | `/cv/` | 实习求职提示、简历下载卡片、`content/cv.md` 联系说明 |
| Life | `/life/` | `content/life.md`，日常照片、故事和小发现 |

- 教育经历、荣誉奖项和学术服务：`content/background.json`，通过 `templates/background.html` 展示在 About 页。
- 个人信息和社交链接：`content/profile.json`。
- 共用页头、导航、页尾和 SEO：`templates/base.html`。
- 首页构图、研究方向卡片和分页标题：`templates/page.html`。
- 样式与响应式断点：`assets/css/site.css`。
- 移动菜单、论文图片放大和旧锚点跳转：`assets/js/site.js`。
- 简历：`docs/潘泽伦_简历.pdf` 与 `docs/PanZelun_Resume.docx`；英文文件保留原有 DOCX 格式。
- 论文图片：放在 `images/`。论文图文区使用 `markdown="1"` 容器，纯图片区使用 `markdown="0"`，以正确处理 HTML 中的 Markdown。
- `_site/` 是可删除的构建产物，每次构建重新生成，不要直接编辑。

导航为真实页面链接。JavaScript 被禁用时仍可以阅读所有页面并使用导航。交互支持键盘、可见焦点和系统“减少动态效果”设置。`/about/`、`/about.html` 会跳到首页，旧版首页各主要章节锚点通过 JavaScript 跳到对应新页面。

## 添加日常生活内容

`Life` 的第一个项目是旅行地图：世界地图按缩放聚合拍摄点，点击标记或地点列表查看附近照片，支持 250 米 / 1 公里 / 5 公里范围和大图浏览。照片区默认收起，选择地图标记或国家／城市后才显示对应照片；点击 Hide photographs 或 Map overview 可再次收起。底图加载失败时仍可通过地点列表浏览照片；选择照片需要 JavaScript，地图底图需要联网。

添加或更新照片：

1. 将带定位的 HEIC / HEIF / JPG 原片放入 `local-photos/travel-originals/`，支持子目录。该目录已被 Git 忽略，构建也不会复制它。
2. 首次导入前，在 `personal_page` 环境安装照片处理依赖。
3. 运行导入脚本，再构建或预览。

```powershell
conda activate personal_page
python -m pip install -r requirements-photos.txt
python scripts/import_travel.py
python scripts/site.py serve
```

脚本从原片读取 GPS 和拍摄日期，修正横竖方向并生成 sRGB JPEG 展示图及缩略图，输出 `images/travel/` 和 `content/travel.json`。相同文件自动去重；无定位照片只进入相册，不猜测拍摄地点。原片不修改。重新导入以当前文件夹内容为准，会移除不再使用的生成图片；请在文件夹中保留仍需展示的照片。空文件夹会报错，避免误清空相册。

地名和图片描述在 `content/travel-labels.json` 中维护，键为相对原片目录的文件名（子目录用 `/`）。这批照片的名称根据坐标和画面整理；新增照片若无名称，先显示经纬度，脚本不调用外部地理编码服务。`content/life.md` 编辑旅行项目介绍，`templates/travel.html` 编辑展示结构。

每张照片用 `country` 维护国家，`city` 保留原有城市或地区标签，`destination` 可单独指定旅行目的地，`place` 保留具体拍摄地点，`alt` 保留画面描述。侧栏按“国家 → 旅行目的地”展示，优先使用 `destination`，未填写时沿用 `city`；点击国家或目的地展示该分类的全部照片。洛杉矶地区、旧金山湾区、巴黎及周边和 Mallorca 按旅行目的地合并，具体城市与景点仍保留在照片数据中。自然风景可以按岛屿或地区组织，尚未确认地点的照片暂保留省级标签，避免猜测。地图图钉仍按距离聚合，顶部 Places 表示地图聚合地点数，不是目的地数。已补充标签但没有 GPS 的照片也能通过索引查看，不会凭空生成精确地图坐标。

无 GPS 的照片可以在标签中添加 `coordinates: [纬度, 经度]`（WGS84）、`location_note`（定位说明）和 `coordinate_reference`（查证来源）。导入优先保留原片 GPS，否则使用手动坐标；手动标记表示地点或附近区域，不代表原始拍摄机位。地图提示和照片预览会显示手动定位说明。

发布时提交生成的图片、清单和网页代码即可，CI 无需 HEIC 依赖。展示图移除了 EXIF，但网页地图清单仍包含实际拍摄坐标。原片保留在本地。

地图使用本地存放的 Leaflet 1.9.4、MapLibre GL 5.6.1 和 Leaflet 适配器 0.1.0（许可证见 `assets/vendor/`），底图为 [OpenFreeMap Liberty](https://openfreemap.org/quick_start/)。矢量样式隐藏海上边界线，保留陆地、道路、地名及地图署名。底图需联网且需要浏览器支持 WebGL；不可用时仍可用地点列表浏览照片。普通页面的脚本和字体仍不依赖 CDN。

## GitHub Pages

工作流位于 `.github/workflows/pages.yml`：

1. 在仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。
2. 本地审阅通过后，将开发分支合并到 `main` 并推送。
3. 工作流安装依赖、执行测试、构建 `_site/`，然后部署到 <https://higgsbose.github.io>。

开发分支 `codex/**` 和针对 `main` 的 PR 只构建和校验，不部署。当前修改不会自动替换线上主页；必须合并到 `main` 且完成上述 Pages 设置。

如果以后部署到项目仓库的子路径，例如 `/personal-page/`，将工作流构建命令改为：

```powershell
python scripts/site.py build --base-path /personal-page --site-url https://higgsbose.github.io
```

默认仓库 `higgsbose.github.io` 不需要 `--base-path`。域名改变时也需更新构建参数和 `robots.txt` / canonical 对应的 `--site-url`。

## 校验

```powershell
python -m unittest discover -s tests -v
python scripts/site.py build
```

自动检查独立路由、当前导航状态、站内链接、图片、简历文件、学术记录迁移、HTML 段落结构、干净构建和 GitHub Pages 子路径支持。外部论文链接保留原始资料，不纳入网络可用性测试。

## 旧版与来源

旧版 Jekyll 文件（`_pages/`、`_layouts/`、`_includes/`、`_sass/`、`_config.yml`、`Gemfile` 等）暂时保留作迁移参考，新构建不读取或发布它们。此前的 `run_server.sh` 已改为调用新的 Python 预览。

原站基于 [AcadHomepage](https://github.com/RayeRen/acad-homepage.github.io)，并使用了 Minimal Mistakes / AcademicPages 的相关资源。原有 LICENSE 保留。Google Scholar 数据抓取工作流保留，新页面不依赖该任务运行。

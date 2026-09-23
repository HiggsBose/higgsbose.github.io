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

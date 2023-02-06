import logging
import os
import glob
import shutil
import re

IN_DIR_PATH = "./in_dir"
OUT_DIR_PATH = "./out_dir"


def transform(in_file, out_file):
    contents = in_file.read()

    html = re.compile(r'[\s\S]*<!DOCTYPE html>')
    contents = html.sub("<!DOCTYPE html>", contents)

    include = re.compile(r'<%@ include file="../(\D*?).jsp"%>')
    contents = include.sub(r'<div th:replace="\1"></div>', contents)

    csh = re.compile(r'<li \D*初始化([^>]*)></li>')
    contents = csh.sub("<li class=\"active\"><span th:text=\"${dzbdmc}\"></span><div th:if=\"${type} eq 'csh'\"><span "
                       "class=\"divider\">>></span>初始化</div></li>", contents)

    skssq = re.compile(r'<li>\S*税款所属期\S*</li>')
    contents = skssq.sub("<li>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;税款所属期：&nbsp;&nbsp;<span th:text=\"${"
                         "skssq}\"></span>&nbsp;&nbsp;&nbsp;&nbsp;</li>", contents)

    meta = re.compile(r'<meta?([^>]*)>')
    contents = meta.sub("", contents)

    cxjs = re.compile(r'<c:if .*sfxsan.*[\s\S]*</c:if>\s*</ul>')
    contents = cxjs.sub("<div th:if=\"${sfxsan} eq '1'\">"
                        "\n<li class=\"right-justified pull-right balloonized\" style=\"margin-top:1px;\">"
                        "\n    <button id='qybgb_save' class=\"an-swlsb btn btn-small btn-primary\">"
                        "\n        <span><font><font>保存</font></font></span> "
                        "\n    </button>"
                        "\n    &nbsp;&nbsp;"
                        "\n    <div th:if=\"${type} eq 'ck'\">"
                        "\n        <button id='recount' class=\"an-swlsb btn btn-small btn-primary\">"
                        "\n            <span>重新计算</span> "
                        "\n        </button>"
                        "\n        &nbsp;&nbsp;"
                        "\n    </div>"
                        "\n</li>"
                        "\n</div>"
                        "\n</ul>", contents)

    session = re.compile(r'<%\s*HttpSession([^>]*)>')
    contents = session.sub("", contents)

    title = re.compile(r'<title>\S*</title>')
    contents = title.sub("", contents)

    icon = re.compile(r'<link\D*type="image/x-icon"([^>]*)>')
    contents = icon.sub("", contents)

    contents = contents.replace("<html>",
                                "<html  lang=\"zh\" xmlns:th=\"http://www.thymeleaf.org\">").replace(
        "<%--", "<!--").replace("--%>", " -->").replace("<%=", "${").replace("%>", "}").replace("</html>", "").replace(
        "<script>", "<script th:inline=\"javascript\">\n/*<![CDATA[*/")

    contents = re.sub(r'[^>]</script>$', "\n /* ]]> */ \n</script>\n</html>", contents)
    contents = re.sub(r'href=[\'\"]?([^\'\"]*)[\'\"]?', r'th:href="@{|\1|}"', contents)
    contents = re.sub(r'src=[\'\"]?([^\'\"]*)[\'\"]?', r'th:src="@{|\1|}"', contents)

    qymc = re.compile(r'<li>[\s\S]*\$\{qymc}[\s\S]*</span></li>')
    contents = qymc.sub("<li><a href=\"\"><span th:text=\"${qymc}\"></span></a><span class=\"divider\">>></span></li>",
                        contents)

    foreach = re.compile(
        r'<c:forEach[\s\S]*?items=\"(\S*?)"[\s\S]*?var="(\S*?)"[\s\S]*?<tr>([\s\S]*?)</tr>[\s\S]*?</c:forEach>')
    contents = foreach.sub(r'<tr th:each="\2 : \1">\n\3\n</tr>', contents)

    td = re.compile(r'<td([\s\S]*?)oldvalue="(\D*?)"(.*?)>(\D*?)</td>')
    contents = td.sub(r'<td \1 \3 th:oldvalue-text="\2"></td>', contents)

    js = contents.split("<script th:inline=\"javascript\">")[1]

    new = re.sub(r'\$\{([^}]*)}', r'[[${\1}]]', js)

    contents = contents.replace(js, new)

    out_file.write(contents)


def main():
    init_logging()

    for in_path in import_path_list(IN_DIR_PATH):
        out_path = generate_out_path(in_path)
        tmp_path = generate_tmp_path(out_path)
        resolve_directories(os.path.dirname(out_path))
        logging.info("transforming {0} -> {1}".format(in_path, out_path))

        with open(in_path, 'r') as in_f:
            with open(tmp_path, 'w') as out_f:
                transform(in_f, out_f)
        shutil.move(tmp_path, out_path)


def init_logging():
    logging.basicConfig(level=logging.INFO)


def import_path_list(in_dir):
    return glob.glob(os.path.join(in_dir, "**/*.jsp"), recursive=True)


def generate_out_path(in_path):
    return os.path.splitext(in_path.replace(IN_DIR_PATH, OUT_DIR_PATH, 1))[0] + ".html"


def generate_tmp_path(in_path):
    return os.path.splitext(in_path)[0] + "_tmp" + os.path.splitext(in_path)[1]


def resolve_directories(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


if __name__ == '__main__':
    main()

import re


def css_to_ts_import(css_file, ts_file):
    """
    Converts @font-face rules in a CSS file to JavaScript import statements and objects,
    while preserving comments at the beginning of the CSS file.

    Args:
      css_file: Path to the CSS file.
      js_file: Path to the output JavaScript file.
    """

    with open(css_file, "r", encoding="utf-8") as f_css, open(ts_file, "w") as f_ts:
        import_count = 0
        font_objects = []
        comments = ""
        reading_comments = True

        for line in f_css:
            if reading_comments:
                if "*/" in line:
                    comments += line
                    reading_comments = False
                else:
                    comments += line
                continue

            match = re.search(r"@font-face\s*{(.*?)}", line, re.DOTALL)
            if match:
                block_content = match.group(1)

                # Extract url
                url_match = re.search(r'url\("?\./(.*?)\"?\)', block_content)
                if url_match:
                    font_file = url_match.group(1)
                    import_statement = (
                        f'import _font{import_count} from "./{font_file}"\n'
                    )
                    f_ts.write(import_statement)

                    # Extract unicode-range
                    unicode_range_match = re.search(
                        r"unicode-range:\s*(.*?);", block_content
                    )
                    unicode_range = (
                        unicode_range_match.group(1) if unicode_range_match else ""
                    )

                    font_object = f"""    {{
        uri: _font{import_count},
        descriptors: {{
            unicodeRange:
            "{unicode_range}",
        }},
    }},"""
                    font_objects.append(font_object)

                    import_count += 1

        # Write comments
        f_ts.write("\n" + comments + "\n")
        f_ts.write("import { type ExcalidrawFontFaceDescriptor } from '../Fonts';\n")

        # Write all font objects
        if font_objects:
            f_ts.write(
                "export const LXGWWenKaiFontFaces: ExcalidrawFontFaceDescriptor[] = [\n"
            )
            for obj in font_objects:
                f_ts.write(obj + "\n")
            f_ts.write("];")


# Example usage
css_file = "./packages/excalidraw/fonts/LXGWWenKai/result.css"  # Replace with your CSS file name
ts_file = "./packages/excalidraw/fonts/LXGWWenKai/index.ts"  # Replace with the desired JS file name
css_to_ts_import(css_file, ts_file)

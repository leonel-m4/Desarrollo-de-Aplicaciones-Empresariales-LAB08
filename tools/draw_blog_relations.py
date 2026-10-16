"""Draw a digital reference for the student's handwritten relationships diagram."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "img"
INK = "#181818"


def font(size, bold=False):
    names = (
        "arialbd.ttf" if bold else "arial.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
    )
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def main():
    image = Image.new("RGB", (2000, 1414), "white")
    draw = ImageDraw.Draw(image)
    title_font = font(40, bold=True)
    heading_font = font(32, bold=True)
    body_font = font(27)
    label_font = font(27, bold=True)
    note_font = font(25)

    def label(position, text, bold=False):
        draw.text(
            position, text, font=label_font if bold else body_font,
            fill=INK, anchor="mm",
        )

    def entity(title, bounds, fields):
        x, y, width, height = bounds
        draw.rectangle((x, y, x + width, y + height), fill="white", outline=INK, width=3)
        draw.rectangle((x + 2, y + 2, x + width - 2, y + 61), fill="#eeeeee")
        draw.line((x, y + 62, x + width, y + 62), fill=INK, width=3)
        draw.text((x + 24, y + 15), title, font=heading_font, fill=INK)
        for index, field in enumerate(fields):
            draw.text(
                (x + 24, y + 84 + index * 36), field,
                font=body_font, fill=INK,
            )

    draw.text(
        (1000, 60), "DIAGRAMA DE RELACIONES - BLOG",
        font=title_font, fill=INK, anchor="mm",
    )
    draw.text(
        (1000, 108), "Referencia digital para copiar a mano; no sustituye tu fotografía.",
        font=note_font, fill=INK, anchor="mm",
    )

    # Connectors are drawn first; their endpoints touch the entity borders.
    for points in (
        [(520, 280), (750, 280)],             # Author -> Post
        [(1250, 280), (1480, 280)],           # Post -> Category
        [(305, 390), (305, 850)],             # Author -> Profile
        [(1000, 580), (1000, 850)],           # Post -> Comment
        [(1250, 470), (1365, 470), (1365, 960), (1480, 960)],  # Post <-> Tag
    ):
        draw.line(points, fill=INK, width=4)

    label((635, 225), "escribe")
    label((548, 254), "1", bold=True)
    label((703, 254), "0..N", bold=True)
    label((1365, 225), "clasifica")
    label((1289, 254), "0..N", bold=True)
    label((1438, 254), "0..1", bold=True)

    label((332, 423), "1", bold=True)
    label((398, 610), "tiene")
    label((351, 820), "0..1", bold=True)

    label((1027, 612), "1", bold=True)
    label((1090, 715), "recibe")
    label((1045, 820), "0..N", bold=True)

    label((1290, 439), "0..N", bold=True)
    label((1493, 637), "tiene etiquetas")
    label((1493, 679), "muchos a muchos")
    label((1438, 930), "0..N", bold=True)

    entity("Author", (90, 170, 430, 220), ["id [PK]", "name"])
    entity("Profile", (90, 850, 430, 300), [
        "id [PK]", "author_id [FK; UQ]", "country", "bio",
    ])
    entity("Post", (750, 170, 500, 410), [
        "id [PK]", "title", "body", "author_id [FK]",
        "category_id [FK; NULL]", "published [bool]",
        "published_at [fecha; NULL]", "tags [relación M:N]",
    ])
    entity("Category", (1480, 170, 430, 220), ["id [PK]", "name [UQ]"])
    entity("Tag", (1480, 850, 430, 220), ["id [PK]", "name [UQ]"])
    entity("Comment", (750, 850, 500, 340), [
        "id [PK]", "post_id [FK]", "author_name [texto; no FK]",
        "text", "created_at [fecha/hora]",
    ])

    for y, text in (
        (1260, "1 = exactamente uno     0..1 = ninguno o uno     0..N = ninguno o muchos"),
        (1300, "PK = clave primaria     FK = clave foránea     UQ = único     NULL = opcional"),
        (1340, "tags no es una columna: Django crea automáticamente la tabla intermedia blog_post_tags."),
    ):
        draw.text((1000, y), text, font=note_font, fill=INK, anchor="mm")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT / "blog_relations_reference.png", dpi=(171, 171))
    image.save(OUTPUT / "blog_relations_reference.pdf", resolution=171)
    print("Created img/blog_relations_reference.png and .pdf")


if __name__ == "__main__":
    main()

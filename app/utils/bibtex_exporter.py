class BibTexExporter:

    @staticmethod
    def export(citation):

        return f"""@article{{{citation.id},
  author = {{{citation.authors}}},
  title = {{{citation.title}}},
  journal = {{{citation.journal or ""}}},
  year = {{{citation.year}}},
  volume = {{{citation.volume or ""}}},
  number = {{{citation.issue or ""}}},
  pages = {{{citation.pages or ""}}},
  doi = {{{citation.doi or ""}}},
  url = {{{citation.url or ""}}}
}}"""

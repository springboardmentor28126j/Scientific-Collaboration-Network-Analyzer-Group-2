class CitationFormatter:

    @staticmethod
    def apa(citation):
        return (
            f"{citation.authors} "
            f"({citation.year}). "
            f"{citation.title}. "
            f"{citation.journal or ''}."
        )

    @staticmethod
    def ieee(citation):
        return (
            f"{citation.authors}, "
            f"\"{citation.title},\" "
            f"{citation.journal or ''}, "
            f"{citation.year}."
        )

    @staticmethod
    def mla(citation):
        return (
            f"{citation.authors}. "
            f"\"{citation.title}.\" "
            f"{citation.journal or ''}, "
            f"{citation.year}."
        )

    @staticmethod
    def chicago(citation):
        return (
            f"{citation.authors}. "
            f"{citation.year}. "
            f"\"{citation.title}.\" "
            f"{citation.journal or ''}."
        )

    @staticmethod
    def harvard(citation):
        return (
            f"{citation.authors} "
            f"({citation.year}) "
            f"{citation.title}. "
            f"{citation.journal or ''}."
        )

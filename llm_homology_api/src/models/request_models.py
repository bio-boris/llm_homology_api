from pydantic import BaseModel, constr, Field, conlist

from config import get_settings

settings = get_settings()


class ProteinSequence(BaseModel):
    id: constr(min_length=5, max_length=settings.MAX_RESIDUE_HEADER_LENGTH) = Field(
        ...,
        description=f"A unique identifier for the protein sequence, with a minimum length of 5 characters and a maximum length of "
        f"{settings.MAX_RESIDUE_HEADER_LENGTH}.",
    )
    sequence: constr(min_length=2, max_length=settings.MAX_RESIDUE_COUNT) = Field(
        ...,
        description=f"A protein sequence with a minimum length of 2 characters and a maximum length of " f"{settings.MAX_RESIDUE_COUNT}.",
    )


class SimilarityRequest(BaseModel):
    sequences: conlist(ProteinSequence, max_length=settings.MAX_PROTEINS_PER_REQUEST) = Field(
        default=[
            ProteinSequence(
                id=">Q5HAN0",
                sequence="MCTSIRHDWQLPEVLELFNLPFNDLILNAHLIHRKFFNSNEIQIAGLLNIKTGGCPENCKYCSQSAHYKTQLKKEDLLNIETIKEAIKKAKVNGIDRFCFAAAWRQIRDRDIEYICNIISLIKSENLESCASLGMVTLEQAKKLKTAGLDFYNHNIDTSRDFYYNVTTTRSYDDRLSSLNNISEAEINICSGGILGLGESIEDRAKMLLTLANLKKHPKSVPINRLVPIKGTPFENNPKISNIDFIRTIAVARILMPESYVRLAAGRESMSHEMQALCLFAGANSLFYGEKLLTTPNADCNDDKNLLSKLGVKTKQAVFFDS",
            ),
            ProteinSequence(
                id=">Q5AYI7",
                sequence="MSVSFTRSFPRAFIRSYGTVQSSPTAASFASRIPPALQEAVAATAPRTNWTRDEVQQIYETPLNQLTYAAAAVHRRFHDPSAIQMCTLMNIKTGGCSEDCSYCAQSSRYSTGLKATKMSPVDDVLEKARIAKANGSTRFCMGAAWRDMRGRKTSLKNVKQMVSGVREMGMEVCVTLGMIDADQAKELKDAGLTAYNHNLDTSREFYPTIITTRSYDERLKTLSHVRDAGINVCSGGILGLGEADSDRIGLIHTVSSLPSHPESFPVNALVPIKGTPLGDRKMISFDKLLRTVATARIVLPATIVRLAAGRISLTEEQQVACFMAGANAVFTGEKMLTTDCNGWDEDRAMFDRWGFYPMRSFEKETNAATPQQHVDSVAHESEKNPAAPAAEAL",
            ),
        ],
        description="A list of protein sequences.",
    )
    threshold: float = Field(
        default=0.8,
        description="Similarity threshold for LLM search. This will prune the results of the search.",
    )
    max_hits: int = Field(default=3, description="Maximum number of hits to return")
    discard_embeddings: bool = Field(
        default=True,
        description="Boolean value to determine whether to discard the embeddings of the queries and hits",
    )

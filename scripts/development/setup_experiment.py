# Poetry Run Python
import protein_search
from protein_search.embedders import get_embedder
from protein_search.search import SimilaritySearch
from pathlib import Path

model_name = "esm2"
pretrained_model_name_or_path = "facebook/esm2_t33_650M_UR50D"

embedder = get_embedder(
    embedder_kwargs={
        # The name of the model architecture to use
        "name": model_name,
        # The model id to use for generating the embeddings
        # Looks like this downloads from the internet? #TODO Ask alex about this
        "pretrained_model_name_or_path": pretrained_model_name_or_path,
        # Use the model in half precision
        "half_precision": True,
        # Set the model to evaluation mode
        "eval_mode": True,
        # Compile the model for faster inference
        # Note: This can actually slow down the inference
        # if the number of queries is small
        "compile_model": False,
    },
)
# In docker volume mounted to /models/sprot_esm_650m_faiss
ss_dataset_dir = "/models/sprot_esm_650m_faiss"

ss = SimilaritySearch(dataset_dir=Path(ss_dataset_dir), embedder=embedder)


query_sequences = [
    "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKRQTLGQHDFSAGEGLYTHMKALRPDEDRLSPLHSVYVDQWDWERVMGDGERQFSTLKSTVEAIWAGIKATEAAVSEEFGLAPFLPDQIHFVHSQELLSRYPDLDAKGRERAIAKDLGAVFLVGIGGKLSDGHRHDVRAPDYDDWSTPSELGHAGLNGDILVWNPVLEDAFELSSMGIRVDADTLKHQLALTGDEDRLELEWHQALLRGEMPQTIGGGIGQSRLTMLLLQLPHIGQVQAGVWPAAVRESVPSLL",
    "XVFGRCELAAAMXRHGLDNYRGYSLGNWVCAAXFESNFNTQATNRNTDGSTDYGILQINSRWWCNDGRTPGSRNLCNIPCSALLSSDITASVNCAXKIVSDGNGMNAWVAWRNRCXGTDVQAWIRGCRL",
]

# run this with ipython
# python -i
# search_results, query_embeddings = ss.search(query_sequences, top_k=10)


# curl -X 'POST' \
#   'localhost:5001/similarity' \
#   -H 'accept: application/json' \
#   -H 'Content-Type: application/json' \
#   -d '{
#   "sequences": [
#     {
#       "id": ">Q5HAN0",
#       "sequence": "MCTSIRHDWQLPEVLELFNLPFNDLILNAHLIHRKFFNSNEIQIAGLLNIKTGGCPENCKYCSQSAHYKTQLKKEDLLNIETIKEAIKKAKVNGIDRFCFAAAWRQIRDRDIEYICNIISLIKSENLESCASLGMVTLEQAKKLKTAGLDFYNHNIDTSRDFYYNVTTTRSYDDRLSSLNNISEAEINICSGGILGLGESIEDRAKMLLTLANLKKHPKSVPINRLVPIKGTPFENNPKISNIDFIRTIAVARILMPESYVRLAAGRESMSHEMQALCLFAGANSLFYGEKLLTTPNADCNDDKNLLSKLGVKTKQAVFFDS"
#     },
#     {
#       "id": ">Q5AYI7",
#       "sequence": "MSVSFTRSFPRAFIRSYGTVQSSPTAASFASRIPPALQEAVAATAPRTNWTRDEVQQIYETPLNQLTYAAAAVHRRFHDPSAIQMCTLMNIKTGGCSEDCSYCAQSSRYSTGLKATKMSPVDDVLEKARIAKANGSTRFCMGAAWRDMRGRKTSLKNVKQMVSGVREMGMEVCVTLGMIDADQAKELKDAGLTAYNHNLDTSREFYPTIITTRSYDERLKTLSHVRDAGINVCSGGILGLGEADSDRIGLIHTVSSLPSHPESFPVNALVPIKGTPLGDRKMISFDKLLRTVATARIVLPATIVRLAAGRISLTEEQQVACFMAGANAVFTGEKMLTTDCNGWDEDRAMFDRWGFYPMRSFEKETNAATPQQHVDSVAHESEKNPAAPAAEAL"
#     }
#   ],
#   "threshold": 0.1,
#   "max_hits": 1,
#   "discard_embeddings": false
# }'

from app.models import Categoria, Marca, Secretaria
from app.schemas.cadastros import (
    CategoriaCreate, CategoriaOut,
    MarcaCreate, MarcaOut,
    SecretariaCreate, SecretariaOut,
)
from app.utils.crud_generico import criar_router_crud_simples

router_categorias = criar_router_crud_simples(
    Categoria, CategoriaCreate, CategoriaOut, "/categorias", "Categorias"
)
router_marcas = criar_router_crud_simples(
    Marca, MarcaCreate, MarcaOut, "/marcas", "Marcas"
)
router_secretarias = criar_router_crud_simples(
    Secretaria, SecretariaCreate, SecretariaOut, "/secretarias", "Secretarias"
)

import asyncio
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy import delete as sql_delete

# Importar aplicación y configuraciones
from app.main import app
from app.infrastructure.db.session import async_session_factory
from app.infrastructure.db.models.catalog import CatalogArticleModel


async def run_manual_test() -> None:
    print("Iniciando prueba de integración manual de endpoints y CRUD...")

    # Generar datos de prueba únicos
    unique_id = uuid.uuid4().hex[:8]
    email = f"test_admin_{unique_id}@example.com"
    password = "Password123!"
    company_name = f"Empresa GEMA {unique_id}"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # =====================================================================
        # 1. Registrar usuario (SaaS Onboarding)
        # =====================================================================
        print("\n--- 1. Probando Registro (SaaS Onboarding) ---")
        register_payload = {
            "data": {
                "type": "users",
                "attributes": {
                    "email": email,
                    "password": password,
                    "nombre": "Administrador de Prueba",
                    "company_name": company_name,
                    "telefono": "+123456789"
                }
            }
        }
        res_register = await client.post(
            "/v1/auth/register",
            json=register_payload,
            headers={"Content-Type": "application/vnd.api+json", "Accept": "application/vnd.api+json"}
        )
        assert res_register.status_code == 201, f"Registro fallido: {res_register.text}"
        print("Usuario registrado exitosamente (onboarding completado).")

        # =====================================================================
        # 2. Iniciar sesión para obtener el token
        # =====================================================================
        print("\n--- 2. Probando Login ---")
        login_payload = {
            "data": {
                "type": "tokens",
                "attributes": {
                    "email": email,
                    "password": password
                }
            }
        }
        res_login = await client.post(
            "/v1/auth/login",
            json=login_payload,
            headers={"Content-Type": "application/vnd.api+json", "Accept": "application/vnd.api+json"}
        )
        assert res_login.status_code == 200, f"Login fallido: {res_login.text}"
        tokens = res_login.json()["data"]["attributes"]
        access_token = tokens["access_token"]
        auth_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json"
        }
        print("Sesión iniciada correctamente. Token JWT obtenido.")

        # =====================================================================
        # 3. Obtener perfil de usuario actual y extraer empresa_id
        # =====================================================================
        print("\n--- 3. Probando Perfil (/v1/auth/me) ---")
        res_me = await client.get("/v1/auth/me", headers=auth_headers)
        assert res_me.status_code == 200, f"Error al consultar perfil: {res_me.text}"
        user_data = res_me.json()["data"]
        empresa_id = user_data["attributes"]["empresa_id"]
        print(f"Perfil del usuario obtenido. Empresa ID vinculada: {empresa_id}")

        # =====================================================================
        # 4. Insertar un artículo de catálogo en base de datos para FK de activo
        # =====================================================================
        print("\n--- 4. Sembrando Artículo de Catálogo (SQL direct insert) ---")
        article_id = uuid.uuid4()
        async with async_session_factory() as session:
            article = CatalogArticleModel(
                id=article_id,
                empresa_id=uuid.UUID(empresa_id),
                nombre="Compresor de Aire Industrial ABC",
                fabricante="Ingersoll Rand",
                modelo="IR-2026",
                unidad_medida="UNIDAD"
            )
            session.add(article)
            await session.commit()
        print(f"Artículo de catálogo sembrado con ID: {article_id}")

        # =====================================================================
        # 5. Crear Ubicación Sede (HEADQUARTERS)
        # =====================================================================
        print("\n--- 5. Probando Crear Ubicación (Sede) ---")
        location_payload = {
            "data": {
                "type": "locations",
                "attributes": {
                    "nombre": "Sede Principal UNEGIA",
                    "tipo": "headquarters",
                    "descripcion": "Oficina principal administrativa"
                }
            }
        }
        res_loc = await client.post(
            f"/v1/companies/{empresa_id}/locations",
            json=location_payload,
            headers=auth_headers
        )
        assert res_loc.status_code == 201, f"Creación de ubicación fallida: {res_loc.text}"
        location_data = res_loc.json()["data"]
        location_id = location_data["id"]
        print(f"Ubicación creada con ID: {location_id} (Tipo: headquarters)")

        # =====================================================================
        # 6. Crear Ubicación Planta (PLANT) como hijo de la Sede
        # =====================================================================
        print("\n--- 6. Probando Crear Ubicación Hijo (Planta) ---")
        sub_location_payload = {
            "data": {
                "type": "locations",
                "attributes": {
                    "nombre": "Planta de Ensamblaje A",
                    "tipo": "plant",
                    "parent_id": location_id,
                    "descripcion": "Línea de producción principal"
                }
            }
        }
        res_sub_loc = await client.post(
            f"/v1/companies/{empresa_id}/locations",
            json=sub_location_payload,
            headers=auth_headers
        )
        assert res_sub_loc.status_code == 201, f"Creación de sub-ubicación fallida: {res_sub_loc.text}"
        sub_location_data = res_sub_loc.json()["data"]
        sub_location_id = sub_location_data["id"]
        print(f"Sub-ubicación creada con ID: {sub_location_id} (Tipo: plant, Parent: {location_id})")

        # =====================================================================
        # 7. Obtener Árbol de Ubicaciones
        # =====================================================================
        print("\n--- 7. Probando Obtener Árbol de Ubicaciones ---")
        res_tree = await client.get(f"/v1/companies/{empresa_id}/locations", headers=auth_headers)
        assert res_tree.status_code == 200, f"Error al obtener árbol: {res_tree.text}"
        tree_data = res_tree.json()["data"]
        assert len(tree_data) > 0, "El árbol debería tener al menos una raíz"
        print(f"Árbol de ubicaciones obtenido exitosamente. Raíces encontradas: {len(tree_data)}")

        # =====================================================================
        # 8. Crear Activo (Asset) vinculado a la Planta
        # =====================================================================
        print("\n--- 8. Probando Crear Activo ---")
        asset_payload = {
            "data": {
                "type": "assets",
                "attributes": {
                    "articulo_id": str(article_id),
                    "serial_interno": f"SN-{unique_id}",
                    "codigo_activo": f"ACT-{unique_id}",
                    "estado": "operational",
                    "ubicacion_id": sub_location_id,
                    "fecha_adquisicion": "2026-06-04",
                    "valor_monetario": 12500.0,
                    "moneda": "USD"
                }
            }
        }
        res_asset = await client.post(
            f"/v1/companies/{empresa_id}/assets",
            json=asset_payload,
            headers=auth_headers
        )
        assert res_asset.status_code == 201, f"Creación de activo fallida: {res_asset.text}"
        asset_data = res_asset.json()["data"]
        asset_id = asset_data["id"]
        print(f"Activo creado exitosamente con ID: {asset_id}")

        # =====================================================================
        # 9. Listar Activos con filtros
        # =====================================================================
        print("\n--- 9. Probando Listar Activos con Filtros ---")
        res_list = await client.get(
            f"/v1/companies/{empresa_id}/assets?estado=operational&ubicacion_id={sub_location_id}",
            headers=auth_headers
        )
        assert res_list.status_code == 200, f"Error al listar activos: {res_list.text}"
        assets_list = res_list.json()["data"]
        assert len(assets_list) > 0, "La lista filtrada debería retornar el activo creado"
        print(f"Lista de activos obtenida y filtrada correctamente. Encontrados: {len(assets_list)}")

        # =====================================================================
        # 10. Actualizar Activo
        # =====================================================================
        print("\n--- 10. Probando Actualizar Activo ---")
        update_payload = {
            "data": {
                "type": "assets",
                "attributes": {
                    "estado": "under_maintenance",
                    "valor_monetario": 13000.0
                }
            }
        }
        res_update = await client.patch(
            f"/v1/companies/{empresa_id}/assets/{asset_id}",
            json=update_payload,
            headers=auth_headers
        )
        assert res_update.status_code == 200, f"Error al actualizar activo: {res_update.text}"
        assert res_update.json()["data"]["attributes"]["estado"] == "under_maintenance"
        print("Activo actualizado correctamente a estado 'under_maintenance'.")

        # =====================================================================
        # 11. Eliminar Activo
        # =====================================================================
        print("\n--- 11. Probando Eliminar Activo ---")
        res_delete_asset = await client.delete(
            f"/v1/companies/{empresa_id}/assets/{asset_id}",
            headers=auth_headers
        )
        assert res_delete_asset.status_code == 204, f"Error al eliminar activo: {res_delete_asset.text}"
        print("Activo eliminado correctamente.")

        # =====================================================================
        # 12. Eliminar Ubicaciones
        # =====================================================================
        print("\n--- 12. Probando Eliminar Ubicaciones ---")
        res_del_sub = await client.delete(
            f"/v1/companies/{empresa_id}/locations/{sub_location_id}",
            headers=auth_headers
        )
        assert res_del_sub.status_code == 204, f"Error al eliminar sub-ubicación: {res_del_sub.text}"
        res_del_parent = await client.delete(
            f"/v1/companies/{empresa_id}/locations/{location_id}",
            headers=auth_headers
        )
        assert res_del_parent.status_code == 204, f"Error al eliminar ubicación padre: {res_del_parent.text}"
        print("Ubicaciones eliminadas correctamente.")

        print("\n=========================================================")
        print("¡TODAS LAS PRUEBAS CRUD Y ENDPOINTS SE COMPLETARON CON ÉXITO!")
        print("=========================================================")


if __name__ == "__main__":
    asyncio.run(run_manual_test())

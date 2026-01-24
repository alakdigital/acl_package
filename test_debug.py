"""
Script de debug pour tester get_by_id localement.
"""

import asyncio
from sqlalchemy import text

# Configuration directe pour le test
import os
os.environ["ACL_DATABASE_TYPE"] = "mysql"
os.environ["ACL_MYSQL_URI"] = "mysql+asyncmy://root:@localhost:3306/acls_db2"
os.environ["ACL_JWT_SECRET_KEY"] = "test-secret-key-for-debugging-minimum-32-chars"
os.environ["ACL_ENABLE_CACHE"] = "false"

from alak_acl.shared.database.mysql import MySQLDatabase
from alak_acl.shared.database.declarative_base import Base
from alak_acl.auth.infrastructure.models.sql_model import SQLAuthUserModel
from alak_acl.auth.infrastructure.repositories.mysql_repository import MySQLAuthRepository
from alak_acl.auth.domain.entities.auth_user import AuthUser
from alak_acl.auth.infrastructure.services.argon2_password_hasher import Argon2PasswordHasher


async def main():
    # 1. Connexion à la base de données
    db_uri = os.environ["ACL_MYSQL_URI"]
    print(f"Connexion à: {db_uri}")

    db = MySQLDatabase(uri=db_uri, echo=True)  # echo=True pour voir les requêtes SQL
    await db.connect()

    # 2. Vérifier les modèles enregistrés dans Base.metadata
    print("\n=== Modèles enregistrés dans Base.metadata ===")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")

    # 3. Créer les tables
    print("\n=== Création des tables ===")
    await db.create_tables()

    # 4. Vérifier que la table existe
    print("\n=== Vérification de la table acl_auth_users ===")
    async with db.session() as session:
        result = await session.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_name = 'acl_auth_users'")
        )
        tables = result.fetchall()
        print(f"Tables trouvées: {tables}")

    # 5. Créer un repository et un utilisateur de test
    print("\n=== Création d'un utilisateur de test ===")
    repo = MySQLAuthRepository(db=db)
    hasher = Argon2PasswordHasher()

    # Créer un utilisateur
    test_user = AuthUser(
        username="testuser_debug",
        email="testuser_debug@example.com",
        hashed_password=hasher.hash("password123"),
    )

    print(f"ID généré pour l'utilisateur: {test_user.id}")
    print(f"Type de l'ID: {type(test_user.id)}")

    try:
        created_user = await repo.create_user(test_user)
        print(f"Utilisateur créé avec succès!")
        print(f"  ID: {created_user.id}")
        print(f"  Username: {created_user.username}")
    except Exception as e:
        print(f"Erreur lors de la création (peut-être déjà existant): {e}")
        # Essayer de récupérer par username
        created_user = await repo.get_by_username("testuser_debug")
        if created_user:
            print(f"Utilisateur existant trouvé par username: {created_user.id}")
        else:
            print("Impossible de trouver l'utilisateur par username non plus!")
            await db.disconnect()
            return

    # 6. Récupérer par ID
    print(f"\n=== Récupération par ID: {created_user.id} ===")

    # Vérifier directement dans la base
    async with db.session() as session:
        result = await session.execute(
            text(f"SELECT id, username FROM acl_auth_users WHERE id = :id"),
            {"id": created_user.id}
        )
        row = result.fetchone()
        print(f"Requête SQL directe - Résultat: {row}")

        if row:
            print(f"  ID dans DB: '{row[0]}' (longueur: {len(row[0])})")
            print(f"  ID recherché: '{created_user.id}' (longueur: {len(created_user.id)})")
            print(f"  Égalité: {row[0] == created_user.id}")
            print(f"  Égalité strip: {row[0].strip() == created_user.id.strip()}")

    # Test via repository
    retrieved_user = await repo.get_by_id(created_user.id)

    if retrieved_user:
        print(f"\nUtilisateur récupéré avec succès!")
        print(f"  ID: {retrieved_user.id}")
        print(f"  Username: {retrieved_user.username}")
    else:
        print(f"\n!!! ERREUR: get_by_id a retourné None !!!")

        # Debug supplémentaire
        print("\n=== Debug supplémentaire ===")
        async with db.session() as session:
            # Lister tous les utilisateurs
            result = await session.execute(text("SELECT id, username FROM acl_auth_users"))
            all_users = result.fetchall()
            print(f"Tous les utilisateurs dans la base:")
            for u in all_users:
                print(f"  - ID: '{u[0]}' | Username: {u[1]}")

    # 7. Nettoyage
    print("\n=== Nettoyage ===")
    await repo.delete_user(created_user.id)
    print("Utilisateur de test supprimé")

    await db.disconnect()
    print("\nTest terminé!")


if __name__ == "__main__":
    asyncio.run(main())

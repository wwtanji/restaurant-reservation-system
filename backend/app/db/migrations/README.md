# Migrations

This directory contains migration scripts used to define changes in the database. These are managed using the Python module [Alembic](https://alembic.sqlalchemy.org/en/latest/), which is designed to work with our ORM module [SQLAlchemy](https://www.sqlalchemy.org/).

The migration source code is located in the [`migrations`](./) directory. Migrations function independently of the ORM schema, which is defined in [`db/orm.py`](../orm.py) and represents the latest (current) version of the application.

The purpose of migrations is to describe how the database evolves across application versions and to automate the application of these changes. This is something the ORM schema cannot do by itself, as it is merely an abstraction over the database and lacks migration capabilities. That’s why an external tool like Alembic is needed — to put it simply, migrations are like "git for the database."

## Managing Migrations

All migrations are managed via the `alembic` command in the terminal. It is platform-independent and works the same on macOS, Linux, and Windows (assuming Alembic is correctly installed in a virtual environment and the venv is activated).

All `alembic` commands must be run from the migrations directory:

```bash
cd backend/db/migrations  # assuming you are in the root directory of the project
```

### Creating a New Migration

Step-by-step process:

1. Modify the ORM schema in [`db/orm.py`](../orm.py) (e.g., add a model, remove an attribute, etc.);
2. Create a new migration:

   ```bash
   alembic revision --autogenerate -m "migration_description"
   ```

3. (Optional) Edit the generated migration file in the [`versions`](./versions) directory if needed;
4. Apply the migration to the database:

   ```bash
   alembic upgrade head
   ```

This command is the most commonly used:

```bash
alembic revision --autogenerate -m "migration_description"
```

Alembic compares the current ORM schema to the current database state and auto-generates a new migration containing all differences. A new file will appear in the [`versions`](./versions) folder. You can manually edit it if the auto-generated script is incorrect. The `-m` flag should include a short English description of what the migration does (e.g., `create_user_table`, `seed_admin`, `add_role_column`, etc.).

To create an empty migration (i.e., without the `--autogenerate` flag), use:

```bash
alembic revision -m "migration_description"
```

In that case, you must manually define the `upgrade` and `downgrade` functions in the generated file.

#### `FAILED: Target database is not up to date.` Error

You need to upgrade the database to the latest version using:

```bash
alembic upgrade head
```

### Applying Migrations

To apply all unapplied migrations, use the `upgrade` command. The argument `head` means "latest version":

```bash
alembic upgrade head
```

**Important:** Once a migration is created and applied, do not modify it. If you need to make changes during local development before merging a pull request, you can downgrade and recreate the corrected migration (see next section).

### Reverting the Last Migration

If a mistake was made and the schema has already been changed, you can revert the database to the previous state by downgrading:

```bash
alembic downgrade -1
```

The `-1` argument means to roll back one migration. This assumes the `downgrade` function is correctly defined in the migration. Otherwise, the command will fail.

### Listing All Migrations

To display all migrations and their status, use:

```bash
alembic history
```

### Creating Seeds

Alembic migrations can also be used to insert default data into the database (known as seeds). See the example in [`versions/56fa62a328fa_seed_admin.py`](./versions/56fa62a328fa_seed_admin.py), which creates an admin user.

Seeds should define essential application data without which the system cannot function (e.g., admin credentials, basic settings, etc.). Do **not** use seeds to insert user-generated or dynamic content (e.g., user accounts, posts, etc.).

## Useful Links

- [Alembic Documentation](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

# Snowflake + dbt Connection Setup

## 1. Get Connection Info from Snowflake Web UI

Run this in Snowflake Worksheets:
```sql
SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE();
```

Copy the results.

---

## 2. Generate RSA Keys

```bash
mkdir -p ~/.snowflake/keys && cd ~/.snowflake/keys
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt
openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub
chmod 600 rsa_key.p8 rsa_key.pub
cat rsa_key.pub
```

Copy the entire public key output (including BEGIN/END lines).

---

## 3. Set Public Key in Snowflake

Run in Snowflake Worksheets (replace with your public key):
```sql
CALL DB_UTILITIES.PUBLIC.p_set_rsa_key_for_current_user('-----BEGIN PUBLIC KEY-----
YOUR_PUBLIC_KEY_HERE
-----END PUBLIC KEY-----');
```

---

## 4. Create `~/.dbt/profiles.yml`

```yaml
my_dbt_project:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: <ACCOUNT_FROM_STEP_1>
      user: <USER_FROM_STEP_1>
      authenticator: SNOWFLAKE_JWT
      private_key_path: /Users/YOUR_USERNAME/.snowflake/keys/rsa_key.p8
      role: <ROLE_FROM_STEP_1>
      warehouse: <WAREHOUSE_FROM_STEP_1>
      database: <DATABASE_FROM_STEP_1>
      schema: PUBLIC
      threads: 4
```

---

## 5. Test Connection

```bash
cd /Users/lehongthai/code_personal/fa-c002-lab/my_dbt_project
source ../.venv/bin/activate
dbt debug
```

Should see: **"All checks passed!"**

---

## Done.

Run dbt commands:
- `dbt run` - Execute models
- `dbt test` - Run tests
- `dbt docs generate && dbt docs serve` - View docs

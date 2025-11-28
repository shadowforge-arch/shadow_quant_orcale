# Shadow Quant Oracle

A full-stack quant signal machine that async-hunts Reddit/Web3 vibes, crunches sentiment with VADER, and ties in live ETH data.

## Setup & Config

1. **Get Keys**: Grab your Reddit `client_id` and `client_secret`.
2. **Inject**: Open `oracle_backend.py` and paste them in the `REDDIT_...` vars.
3. **Install**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Test Run (The Check)
Run a shallow hunt to verify keys and database creation.
```bash
python3 oracle_backend.py --subs quant --depth 2 --vader
```

### 2. The Hunt (Full Scale)
Awaken the swarm.
```bash
python3 oracle_backend.py --subs quant,ethereum,python --depth 50 --vader --web3
```

### 3. The Watch (Dashboard)
Visualize the signals.
```bash
streamlit run streamlit_dashboard.py
```

## Output

*   **shadow_vault.db**: The persistent SQLite database.
*   **oracle_feed.csv**: Raw feed for your backtesting rigs.

*Forged in the dark. Trade at your own risk.*

# Product Description Optimizer

Dette projekt omskriver produkttekster ved hjælp af OpenAI GPT-4o. Du kan behandle CSV- eller Excel-filer og få en ny kolonne med forbedrede beskrivelser.

## Funktioner
- **Bulk-omskrivning** af produktbeskrivelser i et helt regneark.
- **Streamlit-webinterface** til hurtig upload og download.
- **LRU-cache** undgår gentagne API-kald på ens tekster.
- **Progess-bar** via `tqdm` giver status under kørslen.
- Robust håndtering af manglende kolonner eller låste filer.

## Installation
1. Klon repoet.
2. Installer afhængigheder:
   ```bash
   pip install -r requirements.txt
   ```
3. Sæt din OpenAI-nøgle som miljøvariabel:
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```

## CLI-brug
```bash
python product.py input.csv output.csv \
  --input-column "Description" \
  --output-column "Opdateret produkttekst"
```
Programmet gemmer det opdaterede ark som UTF-8 med BOM, så æ, ø og å vises korrekt i Excel.

## API-brug i Python
```python
from product import ProductDescriptionOptimizer
import os

optimizer = ProductDescriptionOptimizer(
    api_key=os.getenv("OPENAI_API_KEY"),
    input_file="./data/product_descriptions.csv",
    output_file="./data/product_descriptions_updated.csv",
)
optimizer.process_csv_file()
```

## Streamlit-webapp
Start den interaktive version:
```bash
streamlit run app.py
```
Her kan du uploade en CSV-fil og ændre prompten direkte i browseren.

## Licens
Distribueres under MIT-licensen. Se `LICENSE` for detaljer.

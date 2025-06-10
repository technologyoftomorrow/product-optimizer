
import os
from functools import lru_cache

import pandas as pd
from openai import OpenAI
from tqdm import tqdm

DEFAULT_PROMPT = """Du er en erfaren SEO-specialist og professionel tekstforfatter, der specialiserer sig i at omskrive produkttekster til webshops. Din opgave er at forbedre eksisterende produktbeskrivelser ud fra følgende kriterier:

1. SEO-optimering: Indarbejd relevante søgeord naturligt i teksten, så den bliver mere synlig i søgemaskiner. Søgeordene skal være relevante for produktkategorien og målgruppen.

2. Fængende og appellerende sprog: Teksterne skal være engagerende og vække interesse hos potentielle kunder. Brug positive, inspirerende og salgsfremmende formuleringer.

3. Præcision og troværdighed: Bevar alle faktuelle oplysninger som tal, måleenheder, produktnavne og branchespecifikke termer præcist som i originalteksten.

4. Læsbarhed og struktur: Omskriv teksten med korte, klare og letlæselige sætninger. Undgå overdreven brug af stjerner, bindestreger og punktopstillinger. Hold teksten sammenhængende og flydende.

4. Unik tekst: Sørg for, at den omskrevne tekst er unik og adskiller sig væsentligt fra originalteksten (mindst 55% nye ord).

Formålet med teksten er at øge kundernes engagement og forbedre konverteringsraten, samtidig med at webshoppens SEO-placering styrkes. Teksterne skal fremstå professionelle, troværdige og rådgivende, så kunden oplever værdi og tryghed ved at handle hos webshoppen. Undgå forklaringer på, hvad du har gjort i teksten; lever blot det færdige resultat uden ekstra kommentarer."""


class ProductDescriptionOptimizer:
    def __init__(self, api_key, input_file=None, output_file=None,
                 input_column="Description", output_column="Opdateret produkttekst",
                 system_prompt: str | None = None):
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key)
        self.input_file = input_file
        self.output_file = output_file
        self.input_column = input_column
        self.output_column = output_column
        self.system_prompt = system_prompt or DEFAULT_PROMPT


    @lru_cache(maxsize=None)
    def generate_seo_text(self, original_text):
        try:
            response = self.client.chat.completions.create(
                model="chatgpt-4o-latest",

                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt,
                    },

                    {
                        "role": "user",
                        "content": f"Omskriv følgende produktbeskrivelse: \n\n{original_text}"
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            new_text = response.choices[0].message.content.strip()
            return new_text
        except Exception as e:
            print(f"Fejl ved generering af tekst for:\n{original_text}\nFejl: {e}")
            return original_text


    def process_excel_file(self):
        """Read an Excel file and write an updated Excel file."""
        try:
            df = pd.read_excel(self.input_file)
        except PermissionError:
            print("Fejl: Filen er åben i et andet program. Luk venligst filen og prøv igen.")
            return
        except Exception as e:
            print(f"Der opstod en fejl ved indlæsning af Excel-filen: {e}")
            return

        if self.input_column not in df.columns:
            # Default til den første kolonne
            self.input_column = df.columns[0]

        print("Kolonnenavne i datafilen:")
        print(df.columns)



        # Process with progress bar
        tqdm.pandas(desc="Opdaterer produkttekster")
        df[self.output_column] = df[self.input_column].progress_apply(self.generate_seo_text)

        try:
            df.to_excel(self.output_file, index=False)
            print(f"Opdaterede produkttekster er gemt i '{self.output_file}'.")

        except Exception as e:
            print(f"Fejl ved lagring af Excel-filen: {e}")

    def process_csv_file(self):
        """Read a CSV file and write an updated CSV file."""
        try:
            df = pd.read_csv(self.input_file)
        except PermissionError:
            print("Fejl: Filen er åben i et andet program. Luk venligst filen og prøv igen.")
            return
        except Exception as e:
            print(f"Der opstod en fejl ved indlæsning af CSV-filen: {e}")
            return

        if self.input_column not in df.columns:
            self.input_column = df.columns[0]

        tqdm.pandas(desc="Opdaterer produkttekster")
        df[self.output_column] = df[self.input_column].progress_apply(self.generate_seo_text)

        try:
            df.to_csv(self.output_file, index=False, encoding="utf-8-sig")
            print(f"Opdaterede produkttekster er gemt i '{self.output_file}'.")
        except Exception as e:
            print(f"Fejl ved lagring af CSV-filen: {e}")

    def process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process an in-memory dataframe and return it with an extra column."""
        if self.input_column not in df.columns:
            self.input_column = df.columns[0]

        tqdm.pandas(desc="Opdaterer produkttekster")
        df[self.output_column] = df[self.input_column].progress_apply(self.generate_seo_text)
        return df

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Optimize product descriptions in a CSV or Excel file")
    parser.add_argument("input_file", help="Path to input CSV or Excel file")
    parser.add_argument("output_file", help="Path to output file")
    parser.add_argument("--input-column", dest="input_column", default="Description", help="Name of the column with original text")
    parser.add_argument("--output-column", dest="output_column", default="Opdateret produkttekst", help="Name of the column to store the updated text")
    parser.add_argument("--instructions", default=DEFAULT_PROMPT, help="Custom system prompt for the language model")
    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is not set")

    optimizer = ProductDescriptionOptimizer(
        api_key=api_key,
        input_file=args.input_file,
        output_file=args.output_file,
        input_column=args.input_column,
        output_column=args.output_column,
        system_prompt=args.instructions,
    )

    if args.input_file.lower().endswith(('.xlsx', '.xls')):
        optimizer.process_excel_file()
    else:
        optimizer.process_csv_file()


import json
import urllib.request

import pandas as pd

DOWNLOADED_FILENAME = "owid-covid-original.csv"
POSTPROCESSED_FILENAME = "owid-covid.csv"
COORDINATES_URL = "https://public.opendatasoft.com/explore/dataset/countries-codes/download/?format=json&timezone=Europe/Berlin&lang=en"


def load_covid_data(remove_aggregates: bool = True) -> pd.DataFrame:
    covid_df = pd.read_csv(DOWNLOADED_FILENAME)

    if remove_aggregates:
        owid_mask = covid_df.iso_code.str.startswith("OWID_")
        covid_df.drop(covid_df[owid_mask].index, inplace=True)

    return covid_df


def load_coords() -> pd.DataFrame:
    with urllib.request.urlopen(COORDINATES_URL, timeout=30) as response:
        coords_df = pd.json_normalize(json.load(response))
        coords_df[["lat", "lon"]] = pd.DataFrame(
            ((None, None) if not isinstance(f, list) else tuple(f) for f in coords_df["fields.geo_point_2d"]),
            index=coords_df.index,
        )
        coords_df.rename(columns={"fields.iso3_code": "iso3"}, inplace=True)

        return coords_df

def main():
    covid_df = load_covid_data()
    coords_df = load_coords()

    final_df = pd.merge(covid_df, coords_df[["iso3", "lon", "lat"]], left_on="iso_code", right_on="iso3")

    final_df.to_csv(POSTPROCESSED_FILENAME)


if __name__ == "__main__":
    main()

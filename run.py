#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Connect to BioRxiv and download annotation associated
with the publications for inclusion in the IMS
"""
import ujson
import requests
import sys
import unidecode
import argparse
import datetime
import csv
import os
import time
import config as cfg

# Initialize Config Variables
downloads_path = cfg.data["download_path"]
source_url = cfg.data["source_url"]


def output_query(outFile, query):
    """ Output the query to the file """
    outFile.write(query + ";\n")


def author_clean(author):
    """ Clean an author and return the formatted string """
    replace = [".", ";", " ", ",", "_"]
    author_split = author.strip().split(",")
    clean_author = ""
    if len(author_split) >= 2:
        last_name = author_split[0]
        first_name = author_split[1]
        for rep in replace:
            first_name = first_name.replace(rep, "")
        clean_author = last_name + " " + first_name
    else:
        for rep in replace:
            clean_author = author.replace(rep, "")

    return unidecode.unidecode(clean_author.strip())


def format_author_short(authors, date):
    """ Create an authors short formatted author entry """
    author = author_clean(authors[0])
    date_split = date.split("-")
    author = author + " (" + date_split[0] + ")"
    return author


def author_short(str1):
    """ Generate a short author name """
    lst = str1.split()
    lastNameLoc = 1
    lastname = lst[-1].title()
    if lastname[0:2].lower() == "jr" or lastname[0:2].lower() == "sr":
        lastname = lst[-2]
        lastNameLoc = 2

    initials = ""

    # traverse in the list
    for i in range(len(lst) - lastNameLoc):
        str1 = lst[i].strip().strip(".,;")

        if len(str1) > 0:
            # If first name or a single character
            if i == 0 or len(str1) == 1 or str1[0].isupper():
                initials += str1[0].upper()
            else:
                lastname = str1 + " " + lastname

    # l[-1] gives last item of list l.
    name = lastname + " " + initials
    return name


def main(args):

    start = int(args.start)

    # Load data from json data file
    dois = set()
    with open(os.path.join(downloads_path, args.input), "r") as infile:
        csv_reader = csv.reader(infile)
        for row in csv_reader:
            dois.add(row[0].strip() + "|" + row[1].strip())

    excel_out = open(os.path.join(downloads_path, args.excel), "w")

    with open(os.path.join(downloads_path, args.output), "w") as outFile:
        for doi in dois:
            doi_split = doi.split("|")
            resp = requests.get(source_url + "/" + doi_split[1] + "/" + doi_split[0])
            if resp.status_code == 200:
                data = ujson.loads(resp.text)
                dataset_details = data["collection"][-1]
                if dataset_details["published"] != "NA":
                    print(
                        doi_split[0]
                        + " is already published at DOI: http://doi.org/"
                        + dataset_details["published"]
                    )
                else:
                    publication = []
                    pubmed_id = "8888" + str(start).zfill(8)
                    publication.append(pubmed_id)
                    publication.append(unidecode.unidecode(dataset_details["title"]))
                    publication.append(
                        unidecode.unidecode(
                            dataset_details["abstract"]
                            .replace("\n", "")
                            .replace('"', "")
                        )
                    )

                    authors = dataset_details["authors"].split(";")
                    authors = [author_clean(author) for author in authors]

                    publication.append(
                        format_author_short(authors, dataset_details["date"])
                    )
                    publication.append(", ".join(authors))

                    publication.append(dataset_details["date"])
                    publication.append(
                        unidecode.unidecode(
                            dataset_details["author_corresponding_institution"]
                        )
                    )
                    publication.append("DOI:" + doi_split[0])

                    query = (
                        'INSERT INTO publications VALUES ("0","%s","%s","%s","%s","%s","0","0","%s","","","%s","%s","active",NULL)'
                        % tuple(publication)
                    )
                    output_query(outFile, query)
                    excel_out.write(pubmed_id + "\t" + doi_split[0] + "\n")

                    start = start + 1

        time.sleep(2)

    excel_out.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Take a set of BioRxiv DOIs and parse them into INSERT statements for the database"
    )

    # Argument to load dois from a file into a list
    parser.add_argument(
        "-i",
        "--input",
        action="store",
        required=True,
        help="Input file containing DOIs for BioRxiv",
    )

    # Argument to output the data into a file for loading in the database
    parser.add_argument(
        "-o", "--output", action="store", required=True, help="Output file for SQL"
    )

    # Argument to output the data into a file for loading in the database
    parser.add_argument(
        "-e", "--excel", action="store", required=True, help="Output file for excel"
    )

    # date to parse to
    parser.add_argument(
        "-s",
        "--start",
        type=int,
        required=True,
        help="Integer to start counting from when generating new biogrid_pubmed ids",
    )

    args = parser.parse_args()
    main(args)

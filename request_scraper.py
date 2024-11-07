import json
import math
import pandas as pd
import requests
from tqdm import tqdm


class RMPSchool:

    def __init__(self, school_id):
        self.school_id = school_id  # school id found using RateMyProfessor
        self.school_name = None  # will be set in _get_num_profs() call within _get_profs_from_sid()
        self.prof_df = self._get_profs_from_sid()  # each entry is a professor
        self.reviews_df = self._get_reviews_for_profs()  # each entry is one review

    def _get_num_profs(self) -> int:
        """
        Gets the number of professors using 'remaining' JSON tag from request.
        Used to know how many pages to look for

        Returns:
        num_profs (int): The number of professors at the university
        """
        profs_page = requests.get(
            "http://www.ratemyprofessors.com/filter/professor/?&page=1&filter=teacherlastname_sort_s+asc&query=\
            *%3A*&queryoption=TEACHER&queryBy=schoolId&sid=" + str(self.school_id))
        prof_content = json.loads(profs_page.content)
        self.school_name = prof_content["professors"][0]["institution_name"]  # get school name from first entry
        num_profs = prof_content['remaining'] + len(prof_content["professors"])  # include results from page1
        return num_profs

    def _get_profs_from_sid(self):
        """
        Gets request from every page in a school's professors list and combines the results into one
        dataframe with one entry per professor
        Returns:
            DataFrame of every professor at the university, along with their aggregate statistics.
        """
        num_pages = math.ceil(self._get_num_profs()/20)  # round up
        print(f"Getting list of professors from {self.school_name}...")
        prof_df = pd.DataFrame()
        with tqdm(total=num_pages) as progress_bar:  # uses a tqdm progress bar
            for page in range(1, num_pages + 1):
                response = requests.get(
                    "http://www.ratemyprofessors.com/filter/professor/?&page=" + str(page) + "&filter=\
                    teacherlastname_sort_s+asc&query=*%3A*&queryoption=TEACHER&queryBy=schoolId&sid="
                    + str(self.school_id)
                )
                prof_content = json.loads(response.content)
                prof_df = pd.concat(
                    [prof_df, pd.DataFrame.from_records(prof_content['professors'])], ignore_index=True
                )
                progress_bar.update(page)
        return prof_df

    def _get_num_reviews(self, prof_id: int):
        """
        Gets the number of reviews for a professor using 'remaining' JSON tag from request.
        Used to know how many pages to look for.
        Args:
            prof_id (int): The RateMyProfessor ID of the professor
        Returns:
            num_reviews(int): The amount of reviews a professor has on RMP
        """
        page1_reviews = requests.get(
            "https://www.ratemyprofessors.com/paginate/professors/ratings?tid=" + str(
                prof_id) + "&filter=&courseCode=&page=1"
        )
        page1_content = json.loads(page1_reviews.content)
        num_reviews = page1_content['remaining'] + len(page1_content["ratings"])  # include results from page1
        return num_reviews

    def _get_reviews_for_prof(self, prof_id: int, num_reviews: int = None):
        """
        Gets all reviews for a specified professor ID
        Args:
            prof_id (int): RateMyProfessor ID of professor you want reviews from
            num_reviews (int): The number of reviews that a professor has, if specified, does not use self.get_num_reviews.
        Returns:
            review_df (pd.DataFrame): Pandas DataFrame where each entry is a review for a professor
        """
        review_df = pd.DataFrame()  # holds all reviews
        num_pages = math.ceil(num_reviews/20) if num_reviews is not None else math.ceil(self._get_num_reviews(prof_id)/20)
        for i in range(1, num_pages + 1):
            response = requests.get("https://www.ratemyprofessors.com/paginate/professors/ratings?tid=" +
                                    str(prof_id) + "&filter=&courseCode=&page=" + str(i))
            page_content = json.loads(response.content)
            review_df = pd.concat(
                [review_df, pd.DataFrame.from_records(page_content["ratings"])], ignore_index=True
            )
        return review_df

    def _get_reviews_for_profs(self):
        """
        Gets reviews for all professors, requires that self.school_id is not None and that get_profs_from_sid has been called
        :return:
        reviews_df (pd.DataFrame): A dataframe holding all reviews for every professor at a school
        """
        if self.school_id is None or self.prof_df.empty:
            print("School ID has not been defined yet or get_profs_from_sid has not been called, "
                  "please instantiate School ID and call get_profs_from_sid")
            return
        print(f"\nGetting reviews for every professor at {self.school_name}...")
        review_df = pd.DataFrame()
        with tqdm(total=self.prof_df.shape[0]) as progress_bar:  # uses a tqdm progress bar
            for prof_id, num_reviews, f_name, l_name, dept in self.prof_df[["tid", "tNumRatings", "tFname", "tLname", "tDept"]].itertuples(
                    index=False, name=None):
                try:
                    prof_df = self._get_reviews_for_prof(prof_id=prof_id, num_reviews=num_reviews)
                    prof_df["tFname"], prof_df["tLname"], prof_df["tDept"] = f_name, l_name, dept
                    review_df = pd.concat([review_df, prof_df], ignore_index=True)
                except json.JSONDecodeError:
                    print(f"\nProfessor with ID:{prof_id} could not be found, moving to next professor...")
                progress_bar.update(1)  # update progress bar
        return review_df

    def dump_to_csv(self) -> bool:
        """
        Takes self.prof_df and self.reviews_df and saves them to CSV files within the current dir.
        :return: True if dataframes were successfully saved to CSV files, false if otherwise
        """
        if self.reviews_df.empty or self.prof_df.empty:
            print(".get_profs_from_sid() or .get_reviews_for_profs() has not been called yet, please"
                  "call them before calling .dum_to_csv()!")
            return False
        school_name = "".join(self.school_name.title().split(" "))  # school name in TitleCase
        self.reviews_df.to_csv(f"{school_name}Reviews.csv")
        self.prof_df.to_csv(f"{school_name}Profs.csv")
        print(f"Review DataFrame successfully saved to {school_name}Reviews.csv")
        print(f"Professor DataFrame successfully saved to {school_name}Profs.csv")
        return True


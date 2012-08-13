import Constants
import csv
import os.path


def main():
    '''
        there was a typo in the edgar module that
        resulted in certain 10-Ks from not being
        downloaded, but they were marked as having
        been gotten. so, we need to perform a sanity
        check that checks each row in the output file
        to make sure that the 10-Ks for a given
        CIK are actually present. if they are, write
        the rows to a new output file.
    '''
    reader = csv.reader(
        open(Constants.PATH_TO_NEW_LITIGATION_FILE, 'rb'),
        delimiter=',')

    writer = csv.writer(
        open(Constants.PATH_TO_NEW_LITIGATION_FILE + "NEW", 'wb'),
        delimiter=',')

    good_ciks = set()
    bad_ciks = set()

    for row in reader:

        CIK = row[2]

        if CIK not in bad_ciks and CIK not in good_ciks:
            candidate_path = os.path.join(Constants.PATH_TO_RAW_URL_DATA, CIK)

            if not os.path.exists(candidate_path):
                print "BAD:", CIK
                bad_ciks.add(CIK)
            else:
                good_ciks.add(CIK)

        if CIK in good_ciks:
            writer.writerow(row)

if __name__ == '__main__':
    main()

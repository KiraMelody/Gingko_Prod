from warcio.archiveiterator import ArchiveIterator
import os
import boto3
import botocore
import csv
import pymysql
import pymysql.cursors
import random

def downloadSegment(remote_path, save_path):
    """Download one segment from Amazon S3.

    Args:
        remote_path: The path where the file is stored on S3.
        save_path: The target path to put the downloaded file.

    Returns:
        None.
    """
    s3 = boto3.resource('s3')
    bucket = s3.Bucket("commoncrawl")
    bucket.download_file(remote_path, save_path)

def loadSiteList(csv_path):
    """Load a list of target sites (either fake or legit).

    Args:
        csv_path: The path to find the CSV file.

    Returns:
        A list of string where each string is a url.
    """
    result = list()
    with open(csv_path) as f:
        csvreader = csv.reader(f)
        for row in csvreader:
            result.append(row[0].lower())
    return result

def matchSite(site_list, a_url):
    """Check whether the given url matches any site in the list.

    Args:
        site_list: A list of string where each string is a url for a site (e.g. https://www.msnbc.com).
        a_url: A url for any web page.

    Returns:
        The matching url string from site_list, or None if no matching is found.
    """
    # return the matching site in the list (if found)
    # return None otherwise
    a_url = a_url.lower()
    for c in site_list:
        if c.lower() in a_url:
            return c
    return None

def storeInSQL(connection, site, http_headers, rec_headers, is_fake, raw_html):
    """Store one record into the database. Below is the data table definition:
    CREATE TABLE `web_pages`(
        `site` TEXT,
        `is_fake` INT,
        `http_headers` MEDIUMTEXT,
        `rec_headers` MEDIUMTEXT,
        `html` MEDIUMTEXT
    );
    
    Args:
        connection: The connection to the database so we can get a cursor from it.
        site: The site (e.g. https://www.msnbc.com) of current record.
        http_headers: HTTP header for current record.
        rec_headers: REC header for current record.
        is_fake: Whether current record is a record of a fake site or not (1 if fake, 0 if not).
        raw_html: The html content of current page.

    Returns:
        None.
    """
    print(site)
    with connection.cursor() as cursor:
        sql = "INSERT INTO `web_pages` VALUES (%s, %s, %s, %s, %s)"
        http_headers_str = str(http_headers)
        rec_headers_str = str(rec_headers)
        cursor.execute(sql, (site, is_fake, http_headers_str, rec_headers_str, raw_html))
    connection.commit()

def storeInSQL2(connection, site, http_headers, rec_headers, raw_html):
    """CREATE TABLE `web_pages2`(
        `site` TEXT,
        `http_headers` MEDIUMTEXT,
        `rec_headers` MEDIUMTEXT,
        `html` MEDIUMTEXT
    );
    """
    with connection.cursor() as cursor:
        sql = "INSERT INTO `web_pages2` VALUES (%s, %s, %s, %s)"
        http_headers_str = str(http_headers)
        rec_headers_str = str(rec_headers)
        cursor.execute(sql, (site, http_headers_str, rec_headers_str, raw_html))
    connection.commit()

def handleOneSegment(warc_file_path, site_list, is_fake=1):
    """Load one Common Crawl segment and save into database all the webpages whose sites can match the ones in site_list.
    The parameter is_fake is to indicate whether site_list is a list of fake sites or legit sites.
    
    Args:
        warc_file_path: The path to the downloaded segment file.
        site_list: A list of URLs that can be loaded using loadSiteList(...) function.
        is_fake: indicate whether site_list is a list of fake sites or legit sites.

    Returns:
        None.
    """
    connection = pymysql.connect(host='localhost',
                                 port=8889,
                                 user='root',
                                 password='root',
                                 db='gingko',
                                 cursorclass=pymysql.cursors.DictCursor)
    with open(warc_file_path, 'rb') as f:
        for record in ArchiveIterator(f):
            if record.rec_type == 'response':
                headers = record.__dict__['http_headers'].headers
                content_type = ""
                for h in headers:
                    if h[0] == 'Content-Type':
                        content_type = h[1]
                        break
                if not content_type.startswith("text/html"):
                    continue
                html = record.content_stream().read().decode("cp437")
                rec_headers = record.__dict__['rec_headers'].headers
                for h in rec_headers:
                    if h[0] == 'WARC-Target-URI':
                        if h[1].startswith("http://") or h[1].startswith("https://"):
                            site = matchSite(site_list, h[1])
                            if site:
                                storeInSQL(connection, site, headers, rec_headers, is_fake, html)
    connection.close()

def handleOneMonth(paths_filepath, site_list, is_fake=1):
    """Common Crawl stores pages it crawled into segments, and publish a 'paths' file that contains pointers to the segments.
    A sample paths file: https://commoncrawl.s3.amazonaws.com/crawl-data/CC-MAIN-2018-47/warc.paths.gz
    This function downloads segments file and runs handleOneSegment(...) function on downloaded segment files one by one.
    
    Args:
        paths_filepath: The path to the downloaded 'paths' file.
        site_list: A list of URLs that can be loaded using loadSiteList(...) function.
        is_fake: indicate whether site_list is a list of fake sites or legit sites.

    Returns:
        None.
    """
    f = open(paths_filepath)
    lines = f.readlines()
    f.close()
    for line in lines:
        l = line[:-1]
        print(l)
        downloadSegment(remote_path=l, save_path="./current.warc.gz")
        print("(downloaded)")
        handleOneSegment("./current.warc.gz", site_list, is_fake)
        os.remove("./current.warc.gz")

site_dict = dict()

def get_site_dict():
    global site_dict
    return site_dict

def download_out_of_list_pages(paths_filepath, site_list):
    global site_dict
    f = open(paths_filepath)
    lines = f.readlines()
    f.close()
    random.shuffle(lines)
    for line in lines[:5]:
        l = line[:-1]
        print(l)
        downloadSegment(remote_path=l, save_path="./current.warc.gz")
        print("(downloaded)")
        #
        connection = pymysql.connect(host='localhost',
                                     port=3306,
                                     user='root',
                                     password='root',
                                     db='gingko',
                                     cursorclass=pymysql.cursors.DictCursor)
        with open("./current.warc.gz", 'rb') as f:
            for record in ArchiveIterator(f):
                if record.rec_type == 'response':
                    headers = record.__dict__['http_headers'].headers
                    content_type = ""
                    for h in headers:
                        if h[0] == 'Content-Type':
                            content_type = h[1]
                            break
                    if not content_type.startswith("text/html"):
                        continue
                    html = record.content_stream().read().decode("cp437")
                    rec_headers = record.__dict__['rec_headers'].headers
                    url = ""
                    site = None
                    for h in rec_headers:
                        if h[0] == 'WARC-Target-URI':
                            if h[1].startswith("http://") or h[1].startswith("https://"):
                                site = matchSite(site_list, h[1])
                                url = h[1]
                                break
                    if site == None:
                        if url.find('/', 9) < 0:
                            continue
                        site = url[:url.find('/', 9)]
                        if site not in site_dict:
                            site_dict[site] = 0
                        if site_dict[site] >= 5:
                            continue
                        site_dict[site] += 1
                        storeInSQL2(connection, site, headers, rec_headers, html)
        connection.close()
        #
        os.remove("./current.warc.gz")

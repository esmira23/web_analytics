import praw
import pandas as pd
import csv
from datetime import datetime, timezone


def auth_params():
    client_id = input("[>] client id: ") 
    client_secret = input("[>] client secret: ") 
    user_agent = input("[>] user agent: ")
    return client_id, client_secret, user_agent


def authentication(client_id, client_secret, user_agent):
    try:
        reddit_client = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
        print("[+] successfully authenticated")
    except Exception as e:
        print("[x] failed to authenticate with error: ", e)
        exit()
    return reddit_client


def scan(reddit_client):
    target_username = input("[>] target account id: ")
    posts_info = []

    redditor = reddit_client.redditor(target_username)
    try:
        submissions = redditor.submissions.new(limit=2000)
    except Exception as e:
        print(f"[x] failed to retrieve submissions for user {target_username}: {e}")
        return posts_info

    for submission in submissions:
        if submission is None:
            continue
        post_text = submission.selftext if submission.is_self and submission.selftext else None
        posts_info.append({
            'author': str(submission.author),
            'title': submission.title,
            'number_of_comments': submission.num_comments,
            'created_time': datetime.fromtimestamp(submission.created_utc, tz=timezone.utc),
            'post_text': post_text,
            'url': submission.url
        })
    return posts_info


def show_results(info):
    if not info:
        print("[x] no posts were found")
    else:
        df = pd.DataFrame(info)
        print(df.head(10))


def save_to_csv(posts_info):
    if not posts_info:
        print("[x] no posts to save")
        return

    file_name = input("[ file name ] : ")
    keys = posts_info[0].keys()
    with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(posts_info)


if __name__ == "__main__":
    client_id, client_secret, user_agent = auth_params()
    reddit_client = authentication(client_id, client_secret, user_agent)
    posts = scan(reddit_client)
    show_results(posts)
    save_to_csv(posts)

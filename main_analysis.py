#! /usr/bin/python
from GitAnalysis import GitAnalysis

if __name__ == '__main__':
    # Initial setup
    log_flag = True
    # fix_commits_file_address_small_samples = r"input/elastic_search_bug_fix_commit_small_samples.txt"
    fix_commits_file_address = r"input/elastic_search_bug_fix_commit.csv"
    repository_address = r"/home/mohsen/git/Human_Factor/Sample_Git_Repository/elasticsearch_copy"
    git_analysis = GitAnalysis(repository_address=repository_address, log_flag=log_flag)

    # End initial setup

    # start export commit messages

    # result_file_address_export_all_commit_messages = r'output/all_commit_messages.json'
    # git_analysis.export_all_commit_messages(result_file_address=result_file_address_export_all_commit_messages)

    # end export commit messages

    # Start Content Analysis
    # analyze_part = 'deleted'
    #
    # result_file_address_content_analysis_fix_commits = r'output/elastic_search_content_analysis_fix_commit_deleted.csv'
    # git_analysis.content_analysis_fix_commits(result_file_address=result_file_address_content_analysis_fix_commits,
    #                                           fix_commits_file_address=fix_commits_file_address,
    #                                           analyze_part=analyze_part)
    #
    # result_file_address_content_analysis_all_commits = r'output/elastic_search_content_analysis_all_commit_deleted.csv'
    # git_analysis.content_analysis_all_commits(result_file_address=result_file_address_content_analysis_all_commits,
    #                                           analyze_part=analyze_part)
    #
    # result_file_address_content_analysis_all_commits_except_fix_commits = \
    #     r'output/elastic_search_content_analysis_all_commit_except_fix_commits_deleted.csv'
    # git_analysis.content_analysis_all_commits_except_fix_commits(
    #     result_file_address=result_file_address_content_analysis_all_commits_except_fix_commits,
    #     fix_commits_file_address=fix_commits_file_address,
    #     analyze_part=analyze_part)

    # End Content Analysis

    # Start Time Analysis Deleted lines

    # result_file_address_time_analysis_fix_commits_deleted_lines = \
    #     r'output/elastic_search_time_analysis_deleted_lines_fix_commits.csv'
    # git_analysis.time_analysis_deleted_lines_fix_commits(
    #      result_file_address=result_file_address_time_analysis_fix_commits_deleted_lines,
    #      fix_commits_file_address=fix_commits_file_address)

    # executed up to hear

    # result_file_address_time_analysis_deleted_lines_all_commits = \
    #     r'output/elastic_search_time_analysis_deleted_lines_all_commits.csv'
    # git_analysis.time_analysis_deleted_lines_all_commits(
    #     result_file_address=result_file_address_time_analysis_deleted_lines_all_commits)
    #
    # result_file_address_time_analysis_deleted_lines_all_commit_except_fix_commits = \
    #     r'output/elastic_search_time_analysis_deleted_lines_all_commits.csv'
    # git_analysis.time_analysis_deleted_lines_all_commit_except_fix_commits(
    #     result_file_address=result_file_address_time_analysis_deleted_lines_all_commit_except_fix_commits,
    #     fix_commits_file_address=fix_commits_file_address)

    # End Time Analysis Deleted lines

    # Start Time Analysis

    # result_file_address_time_analysis_all_commits = \
    #     r"output/elastic_search_time_analysis_all_commits.csv"
    # git_analysis.time_analysis_all_commits(result_file_address_time_analysis_all_commits)
    #
    # result_file_address_time_analysis_fix_commits = r"output/elastic_search_time_analysis_fix_commits.csv"
    # git_analysis.time_analysis_fix_commits(result_file_address_time_analysis_fix_commits, fix_commits_file_address)
    #
    # result_file_address_time_analysis_all_commit_except_fix_commits = \
    #     r"output/elastic_search_time_analysis_all_commits_except_fix_commits.csv"
    # git_analysis.time_analysis_all_commits_except_fix_commits(
    #     result_file_address_time_analysis_all_commit_except_fix_commits,
    #     fix_commits_file_address)

    # End Time Analysis

    # Start Change Analysis

    # result_file_address_fix_commit_changes = r"output/elastic_search_change_count_fix_commits.csv"
    # git_analysis.count_change_fix_commits(result_file_address=result_file_address_fix_commit_changes,
    #                                       fix_commits_file_address=fix_commits_file_address)
    #
    # result_file_address_changes_all_commits = r"output/elastic_search_change_count_all_commits.csv"
    # git_analysis.count_change_all_commits(result_file_address=result_file_address_changes_all_commits)
    #
    # result_file_address_changes_all_commits_except_fix_commits = \
    #     r"output/elastic_search_change_count_all_commits_except_fix_commits.csv"
    # git_analysis.count_change_all_commits_except_fix_commits(
    #     result_file_address=result_file_address_changes_all_commits_except_fix_commits,
    #     fix_commits_file_address=fix_commits_file_address)
    #
    # result_file_address_changes_all_commits_limited_files_except_fix_commits = \
    #     r"output/_elastic_search_change_count_all_commits_limited_files_except_fix_commits.csv"
    # git_analysis.count_change_all_commits_limited_files_except_fix_commit(
    #     result_file_address=result_file_address_changes_all_commits_limited_files_except_fix_commits,
    #     fix_commits_file_address=fix_commits_file_address)

    # End Change Analysis

    # git_analysis.count_commit()

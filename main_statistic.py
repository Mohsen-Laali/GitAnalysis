from GitAnalysis import StatisticalAnalyzer


if __name__ == '__main__':
    csv_file = r'output/copy_elastic_search_time_analysis_deleted_lines_fix_commits.csv'
    log_flag = False
    statistical_analyzer = StatisticalAnalyzer(log_flag=log_flag)

    # # Frequency Count
    # file_name = r'output/back_up_9_oct/elastic_search_content_analysis_fix_commit_deleted.csv'
    # keep_dictionary = {'lexer_name': 'Java', }
    # count_column_limited = ['token_type']
    # result_file_address = r'output/stat_f/stat_frequency_content_fix_commits_deleted_tokenType.csv'
    # statistical_analyzer.find_frequency(file_name=file_name, result_file_address=result_file_address,
    #                                     count_column_limited=count_column_limited, keep_dictionary=keep_dictionary)
    #
    # count_column_limited = ['token_content']
    # result_file_address = r'output/stat_f/stat_frequency_content_fix_commits_deleted_tokenContent.csv'
    # statistical_analyzer.find_frequency(file_name=file_name, result_file_address=result_file_address,
    #                                     count_column_limited=count_column_limited, keep_dictionary=keep_dictionary)
    #
    # print 'Frequency fix commits finished'
    #
    # file_name = r'output/elastic_search_content_analysis_all_commit_except_fix_commits_deleted.csv'
    # keep_dictionary = {'lexer_name': 'Java', }
    # count_column_limited = ['token_type']
    # result_file_address = r'output/stat_f/stat_frequency_content_all_commit_except_fix_commits_deleted_tokenType.csv'
    # statistical_analyzer.find_frequency(file_name=file_name, result_file_address=result_file_address,
    #                                     count_column_limited=count_column_limited, keep_dictionary=keep_dictionary)
    #
    # count_column_limited = ['token_content']
    # result_file_address = r'output/stat_f/' \
    #                       r'stat_frequency_content_all_commit_except_fix_commits_deleted_tokenContent.csv'
    # statistical_analyzer.find_frequency(file_name=file_name, result_file_address=result_file_address,
    #                                     count_column_limited=count_column_limited, keep_dictionary=keep_dictionary)

    # print 'Frequency all commits finished'
    # End frequency count

    # Start frequency count sub group

    # file_name = r'output/back_up_9_oct/elastic_search_content_analysis_fix_commit_deleted.csv'
    # keep_dictionary = {'lexer_name': 'Java'}
    # group_column = 'token_type'
    # count_sub_column = 'token_content'
    # count_sub_exception = []
    # result_file_address = r'output/stat_f/sub_stat_frequency_content_fix_commits_deleted.csv'
    # statistical_analyzer.find_frequency_sub_group(file_name=file_name, result_file_address=result_file_address,
    #                                               group_column=group_column, count_sub_column=count_sub_column,
    #                                               keep_dictionary=keep_dictionary,
    #                                               count_sub_exception=count_sub_exception)
    #
    # file_name = r'output/elastic_search_content_analysis_all_commit_except_fix_commits_deleted.csv'
    # keep_dictionary = {'lexer_name': 'Java'}
    # group_column = 'token_type'
    # count_sub_column = 'token_content'
    # count_sub_exception = []
    # result_file_address = r'output/stat_f/sub_stat_frequency_content_all_commit_except_fix_commits_deleted.csv'
    # statistical_analyzer.find_frequency_sub_group(file_name=file_name, result_file_address=result_file_address,
    #                                               group_column=group_column, count_sub_column=count_sub_column,
    #                                               keep_dictionary=keep_dictionary,
    #                                               count_sub_exception=count_sub_exception)

    # End frequency count sub group

    # Start frequency language
    # file_name = r'output/back_up_9_oct/elastic_search_content_analysis_fix_commit_deleted.csv'
    # keep_dictionary = {'lexer_name': 'Java', 'token_type': ['Token.Keyword.Declaration',
    #                                                         'Token.Keyword.Namespace',
    #                                                         'Token.Keyword',
    #                                                         'Token.Keyword.Type']}
    # count_column_limited = ['token_content']
    # result_file_address = r'output/stat_f/stat_frequency_content_fix_commits_deleted_language.csv'
    # aggregate_column = 'hex_hash'
    # statistical_analyzer.find_frequency_normalized_count(file_name=file_name, result_file_address=result_file_address,
    #                                                      count_column_limited=count_column_limited,
    #                                                      aggregate_column=aggregate_column,
    #                                                      keep_dictionary=keep_dictionary)

    # statistical_analyzer.find_frequency(file_name=file_name, result_file_address=result_file_address,
    #                                     count_column_limited=count_column_limited, keep_dictionary=keep_dictionary)
    #
    # file_name = r'output/elastic_search_content_analysis_all_commit_except_fix_commits_deleted.csv'
    # keep_dictionary = {'lexer_name': 'Java', 'token_type': ['Token.Keyword.Declaration',
    #                                                            'Token.Keyword.Namespace',
    #                                                            'Token.Keyword',
    #                                                            'Token.Keyword.Type']}
    # count_column_limited = ['token_content']
    # result_file_address = r'output/stat_f/stat_frequency_content_all_commit_except_fix_commits_deleted_language.csv'
    # aggregate_column = 'hex_hash'
    # statistical_analyzer.find_frequency_normalized_count(file_name=file_name, result_file_address=result_file_address,
    #                                                      count_column_limited=count_column_limited,
    #                                                      aggregate_column=aggregate_column,
    #                                                      keep_dictionary=keep_dictionary)
    # statistical_analyzer.find_frequency(file_name=file_name, result_file_address=result_file_address,
    #                                     count_column_limited=count_column_limited, keep_dictionary=keep_dictionary)
    # print 'Language frequency finished !!!'
    # # End frequency language

    # # Start frequency project level
    # file_name = r'output/back_up_9_oct/elastic_search_content_analysis_fix_commit_deleted.csv'
    # keep_dictionary = {'lexer_name': 'Java', 'token_type': ['Token.Name.Function', 'Token.Name.Class',
    #                                                            'Token.Name.Namespace']}
    #
    # count_column_limited = ['token_content']
    # result_file_address = r'output/stat_f/stat_frequency_content_fix_commits_deleted_project_level.csv'
    # aggregate_column = 'hex_hash'
    # statistical_analyzer.find_frequency_normalized_count(file_name=file_name, result_file_address=result_file_address,
    #                                                      count_column_limited=count_column_limited,
    #                                                      aggregate_column=aggregate_column,
    #                                                      keep_dictionary=keep_dictionary)
    # statistical_analyzer.find_frequency(file_name=file_name, result_file_address=result_file_address,
    #                                     count_column_limited=count_column_limited, keep_dictionary=keep_dictionary)
    #
    # file_name = r'output/elastic_search_content_analysis_all_commit_except_fix_commits_deleted.csv'
    # keep_dictionary = {'lexer_name': 'Java', 'token_type': ['Token.Name.Function', 'Token.Name.Class',
    #                                                            'Token.Name.Namespace']}
    #
    # count_column_limited = ['token_content']
    # result_file_address = r'output/stat_f/' \
    #                       r'stat_frequency_content_all_commit_except_fix_commits_deleted_project_level.csv'
    # aggregate_column = 'hex_hash'
    # statistical_analyzer.find_frequency_normalized_count(file_name=file_name, result_file_address=result_file_address,
    #                                                      count_column_limited=count_column_limited,
    #                                                      aggregate_column=aggregate_column,
    #                                                      keep_dictionary=keep_dictionary)
    # statistical_analyzer.find_frequency(file_name=file_name, result_file_address=result_file_address,
    #                                     count_column_limited=count_column_limited, keep_dictionary=keep_dictionary)
    # print 'Project level frequency finished !!!'
    # End frequency project level

    # End aggregated count

    # Start language frequency per line
    # file_name = r'output/back_up_9_oct/elastic_search_content_analysis_fix_commit_deleted.csv'
    # keep_dictionary = {'lexer_name': 'Java', 'token_type': ['Token.Keyword.Declaration',
    #                                                         'Token.Keyword.Namespace',
    #                                                         'Token.Keyword',
    #                                                         'Token.Keyword.Type']}
    # flag_binary_count_normalized = True
    # flag_aggregate_count_normalize = True
    # count_column_limited = ['token_content']
    # result_file_address = \
    #     r'output/stat_f/per_line_stat/stat_frequency_per_line_content_fix_commits_deleted_language.csv'
    # aggregate_column = 'hex_hash'
    # statistical_analyzer.find_frequency_per_line_aggregated(
    #     file_name=file_name, result_file_address=result_file_address, count_column_limited=count_column_limited,
    #     aggregate_column=aggregate_column, keep_dictionary=keep_dictionary,
    #     flag_binary_count_normalized=flag_binary_count_normalized,
    #     flag_aggregate_count_normalize=flag_aggregate_count_normalize)
    #
    # file_name = r'output/elastic_search_content_analysis_all_commit_except_fix_commits_deleted.csv'
    # keep_dictionary = {'lexer_name': 'Java', 'token_type': ['Token.Keyword.Declaration',
    #                                                            'Token.Keyword.Namespace',
    #                                                            'Token.Keyword',
    #                                                            'Token.Keyword.Type']}
    # flag_binary_count_normalized = True
    # flag_aggregate_count_normalize = True
    # count_column_limited = ['token_content']
    # result_file_address = \
    #     r'output/stat_f/per_line_stat/' \
    #     r'stat_frequency_per_line_content_all_commit_except_fix_commits_deleted_language.csv'
    # aggregate_column = 'hex_hash'
    # statistical_analyzer.find_frequency_per_line_aggregated(
    #     file_name=file_name, result_file_address=result_file_address,
    #     count_column_limited=count_column_limited,
    #     aggregate_column=aggregate_column, keep_dictionary=keep_dictionary,
    #     flag_binary_count_normalized=flag_binary_count_normalized,
    #     flag_aggregate_count_normalize=flag_aggregate_count_normalize)
    # print 'Language frequency per line finished !!!'
    # # End language frequency per line
    #
    # # Start project level per line
    # file_name = r'output/back_up_9_oct/elastic_search_content_analysis_fix_commit_deleted.csv'
    # keep_dictionary = {'lexer_name': 'Java', 'token_type': ['Token.Name.Function', 'Token.Name.Class',
    #                                                         'Token.Name.Namespace']}
    # flag_binary_count_normalized = True
    # flag_aggregate_count_normalize = True
    # count_column_limited = ['token_content']
    # result_file_address = \
    #     r'output/stat_f/per_line_stat/stat_frequency_per_line_content_fix_commits_deleted_project_level.csv'
    # aggregate_column = 'hex_hash'
    # statistical_analyzer.find_frequency_per_line_aggregated(
    #     file_name=file_name, result_file_address=result_file_address,
    #     count_column_limited=count_column_limited,
    #     aggregate_column=aggregate_column, keep_dictionary=keep_dictionary,
    #     flag_binary_count_normalized=flag_binary_count_normalized,
    #     flag_aggregate_count_normalize=flag_aggregate_count_normalize)

    file_name = r'output/elastic_search_content_analysis_all_commit_except_fix_commits_deleted.csv'
    keep_dictionary = {'lexer_name': 'Java', 'token_type': ['Token.Name.Function', 'Token.Name.Class',
                                                            'Token.Name.Namespace']}
    flag_binary_count_normalized = True
    flag_aggregate_count_normalize = True
    count_column_limited = ['token_content']
    result_file_address = r'output/stat_f/per_line_stat/' \
                          r'stat_frequency_per_line_content_all_commit_except_fix_commits_deleted_project_level.csv'
    aggregate_column = 'hex_hash'
    statistical_analyzer.find_frequency_per_line_aggregated(
        file_name=file_name, result_file_address=result_file_address,
        count_column_limited=count_column_limited,
        aggregate_column=aggregate_column, keep_dictionary=keep_dictionary,
        flag_binary_count_normalized=flag_binary_count_normalized,
        flag_aggregate_count_normalize=flag_aggregate_count_normalize)

    print 'Language project level per line finished !!!'
    # End project level per line

    # Start project per line



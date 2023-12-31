if 'team' in matches_rolling.index.names:
    matches_rolling = matches_rolling.droplevel('team')

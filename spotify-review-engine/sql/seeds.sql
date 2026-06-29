-- ============================================================
-- seeds.sql — Seed themes and user_segments taxonomy
-- Run AFTER schema.sql
-- ============================================================

-- ============================================================
-- THEMES
-- ============================================================

-- Group: discovery_frictions
insert into themes (theme_code, theme_name, theme_group, theme_description) values
('repetitive_recommendations',   'Repetitive Recommendations',  'discovery_frictions', 'Algorithm keeps recommending the same artists or tracks the user already knows well.'),
('weak_novelty',                 'Weak Novelty',                'discovery_frictions', 'Recommendations do not introduce genuinely new or unfamiliar content.'),
('playlist_overdependence',      'Playlist Overdependence',     'discovery_frictions', 'User relies entirely on curated playlists rather than organic discovery.')
on conflict (theme_code) do nothing;

-- Group: behavioral_intent
insert into themes (theme_code, theme_name, theme_group, theme_description) values
('passive_discovery',      'Passive Discovery',      'behavioral_intent', 'User wants music discovered for them without active effort.'),
('active_exploration',     'Active Exploration',     'behavioral_intent', 'User actively seeks out new genres, artists, or sounds.'),
('social_discovery',       'Social Discovery',       'behavioral_intent', 'User discovers music through friends, social sharing, or community.'),
('genre_expansion',        'Genre Expansion',        'behavioral_intent', 'User wants to branch out into adjacent or unfamiliar genres.')
on conflict (theme_code) do nothing;

-- Group: repetition_triggers
insert into themes (theme_code, theme_name, theme_group, theme_description) values
('comfort_listening',           'Comfort Listening',           'repetition_triggers', 'User deliberately returns to familiar music for comfort or safety.'),
('habit_loop',                  'Habit Loop',                  'repetition_triggers', 'Listening to the same content has become an unconscious habit.')
on conflict (theme_code) do nothing;

-- Group: unmet_needs
insert into themes (theme_code, theme_name, theme_group, theme_description) values
('novelty_control',        'Novelty Control',        'unmet_needs', 'User wants a dial or setting to control how adventurous recommendations are.'),
('reset_recommendations',  'Reset Recommendations',  'unmet_needs', 'User wants to clear or reset their listening history and algorithm state.')
on conflict (theme_code) do nothing;

-- ============================================================
-- USER SEGMENTS
-- ============================================================
insert into user_segments (segment_code, segment_name, segment_description) values
('passive_familiar_listener',   'Passive Familiar Listener',   'Listens passively to familiar, comfortable music. Low motivation to actively discover. Tends to replay saved playlists and liked songs.'),
('playlist_reliant_listener',   'Playlist-Reliant Listener',   'Relies almost exclusively on curated playlists (Discover Weekly, Release Radar, editorial). Does not actively search for new music.'),
('active_explorer',             'Active Explorer',             'Actively seeks new music, genres, and artists. Uses search, radio, and recommendation features intentionally.'),
('mood_context_listener',       'Mood / Context Listener',     'Selects music based on current mood, activity, or context (working, running, relaxing). Highly context-dependent listening patterns.'),
('social_discovery_listener',   'Social Discovery Listener',   'Discovers music primarily through friends, social sharing, concerts, or social media. Values peer-validated discovery.')
on conflict (segment_code) do nothing;

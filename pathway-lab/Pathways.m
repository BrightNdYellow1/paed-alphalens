let
    // Set PathwaysCsv to the full path of the curated CSV.
    Source = Csv.Document(File.Contents(PathwaysCsv),
        [Delimiter=",", Columns=8, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Nullable = Table.ReplaceValue(Headers, "", null, Replacer.ReplaceValue,
        {"first_attendance_date", "wait_days"}),
    Types = Table.TransformColumnTypes(Nullable,
        {{"referral_id", type text}, {"site", type text}, {"specialty", type text},
         {"referral_date", type date}, {"first_attendance_date", type date},
         {"status", type text}, {"wait_days", Int64.Type}, {"referral_month", type text}},
        "en-GB")
in
    Types

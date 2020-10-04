from nextinspace import api, parser, space, viewer


def main():
    args = parser.get_args()

    if args.verbose:
        VERBOSITY = space.Verbosity.VERBOSE
    elif args.quiet:
        VERBOSITY = space.Verbosity.QUIET
    else:
        VERBOSITY = space.Verbosity.NORMAL

    if args.events_only:
        events = api.get_events(args.num_items)
        viewer.display_list(events, VERBOSITY)
    if args.launches_only:
        launches = api.get_launches(args.num_items)
        viewer.display_list(launches, VERBOSITY)


if __name__ == "__main__":
    main()

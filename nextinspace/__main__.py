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
        items = api.get_events(args.num_items)
    elif args.launches_only:
        items = api.get_launches(args.num_items, VERBOSITY)
    else:
        items = api.get_all(args.num_items, VERBOSITY)

    viewer.display_list(items, VERBOSITY)


if __name__ == "__main__":
    main()

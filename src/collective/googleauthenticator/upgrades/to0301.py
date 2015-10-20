
def upgrade(setup_context):
    setup_context.runImportStepFromProfile(
        'profile-collective.googleauthenticator.upgrades:0301',
        'actions',
        run_dependencies=False,
        purge_old=False)

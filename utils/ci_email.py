import os
from pathlib import Path

from utils.email_notifier import send_email
from utils.logger import get_logger


logger = get_logger(__name__)


def main() -> int:
    required = ("SMTP_HOST", "EMAIL_TO", "EMAIL_USERNAME", "EMAIL_PASSWORD")
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        logger.warning("CI email skipped; missing configuration: %s", ", ".join(missing))
        return 0

    username = os.environ["EMAIL_USERNAME"]
    os.environ["SMTP_USERNAME"] = username
    os.environ["SMTP_PASSWORD"] = os.environ["EMAIL_PASSWORD"]

    status = os.getenv("EXECUTION_STATUS", "unknown").upper()
    repository = os.getenv("REPOSITORY", "unknown")
    workflow = os.getenv("WORKFLOW_NAME", "Playwright Python Tests")
    run_number = os.getenv("RUN_NUMBER", "unknown")
    run_url = os.getenv("RUN_URL", "unavailable")
    artifact_url = os.getenv("REPORT_ARTIFACT_URL", "").strip() or "unavailable"
    report_path = Path(os.getenv("REPORT_PATH", "report.html"))

    body = "\n".join(
        (
            f"Execution status: {status}",
            f"Repository: {repository}",
            f"Workflow: {workflow} (run #{run_number})",
            f"Workflow run: {run_url}",
            f"HTML report artifact: {artifact_url}",
        )
    )

    attachments: list[Path] = []
    if report_path.is_file():
        attachments.append(report_path)
    else:
        logger.warning("HTML report is unavailable for email attachment: %s", report_path)

    send_email(
        subject=f"{status}: Playwright tests for {repository}",
        body=body,
        attachments=attachments,
    )
    logger.info("CI test summary email sent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import logging

def log_section_header(logger, title: str) -> None:
    """Log a major section header with consistent formatting and green color.
    
    Args:
        logger: The logger instance to use
        title: The title text for the section header
    """
    # Define green color code
    GREEN = '\033[92m'  # Bright green
    RESET = '\033[0m'   # Reset to default
    
    # Use error level for headers containing "FAILED" or "ERROR", warning for "WARNING", otherwise green
    if "FAILED" in title or "ERROR" in title:
        logger.error(f"{title}")
    elif "WARNING" in title:
        logger.warning(f"{title}")
    else:
        # For normal headers, use info level with green color
        logger.info(f"{GREEN}{title}{RESET}")

def log_step(logger, step_number: int, total_steps: int, description: str, header: bool=False) -> None:
    """Log a numbered step in a multi-step process.
    
    Args:
        logger: The logger instance to use
        step_number: Current step number
        total_steps: Total number of steps
        description: Description of the current step
        header: Whether to apply header formatting (default: False)
    """
    # Define color codes
    GREEN = '\033[92m'  # Bright green
    RESET = '\033[0m'   # Reset to default

    if header:
        logger.info(f"{GREEN}Step {step_number}/{total_steps}: {description}{RESET}")
    else:
        logger.info(f"Step {step_number}/{total_steps}: {description}")

def log_step_result(logger, success: bool, message: str, details: str = None) -> None:
    """Log the result of a step with visual indicator.
    
    Args:
        logger: The logger instance to use
        success: Whether the step was successful
        message: Result message
        details: Optional additional details (default: None)
    """
    # Define color codes
    GREEN = '\033[92m'  # Bright green
    RED = '\033[91m'    # Red
    RESET = '\033[0m'   # Reset to default
    
    # Apply appropriate color to the prefix symbol
    if success:
        prefix = f"{GREEN}✓{RESET}"
        logger.info(f"{prefix} {message}")
    else:
        prefix = f"{RED}✗{RESET}"
        # For failed steps, use error level to trigger red coloring
        logger.error(f"{prefix} {message}")
    
    if details:
        level = logging.INFO if success else logging.ERROR
        logger.log(level, f"  - {details}")

def log_warning(logger, message: str) -> None:
    """Log a warning message with a warning symbol.
    
    Args:
        logger: The logger instance to use
        message: Warning message to log
    """
    # Define yellow color for warning symbol
    YELLOW = '\033[93m'  # Yellow
    RESET = '\033[0m'    # Reset to default
    
    # Add yellow color to the warning symbol
    logger.warning(f"{YELLOW}⚠{RESET} {message}")
from .implementation import CSVAgentHandlerImplementation
class CSVAgentHandler:
    """
    Handles interaction with a CSV-based AI agent.
    """
    def __init__(self, csv_files, model=None, verbose=True, agent_type=None):

        """
        Initialize the CSV agent.
        :param csv_files: Path to one or more CSV files (string or list).
        :param model: Instance of a chat model (e.g., ChatOpenAI or AzureChatOpenAI).
        :param verbose: Show detailed logs if True.
        :param agent_type: Type of agent to use. Defaults to OPENAI_FUNCTIONS if not specified.
        """
        self.csv_files = csv_files
        self.model = model
        self.verbose = verbose

        self._impl = CSVAgentHandlerImplementation(
            csv_files=self.csv_files,
            model=self.model,
            verbose=self.verbose,
            agent_type=agent_type
        )
        


    def ask_question(self, query):
        """
        Ask a question to the CSV agent.
        :param query: Question to ask about the CSV data.
        :return: Answer from the agent.
        """
        return self._impl.ask_question(query)
    
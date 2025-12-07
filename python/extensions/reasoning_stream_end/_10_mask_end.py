from python.helpers.extension import Extension


class MaskReasoningStreamEnd(Extension):
    """
    An extension that finalizes the reasoning stream masking process. This is
    called after the reasoning stream has ended.
    """
    async def execute(self, **kwargs):
        """
        Executes the reasoning stream end masking extension.

        This method finalizes the streaming filter, which may process and
        output any remaining buffered text. It then cleans up the filter
        instance from the agent's data.

        Args:
            **kwargs: Arbitrary keyword arguments. Expected to contain 'agent'.
        """
        # Get agent and finalize the streaming filter
        agent = kwargs.get("agent")
        if not agent:
            return

        try:
            # Finalize the reasoning stream filter if it exists
            filter_key = "_reason_stream_filter"
            filter_instance = agent.get_data(filter_key)
            if filter_instance:
                tail = filter_instance.finalize()

                # Print any remaining masked content
                if tail:
                    from python.helpers.print_style import PrintStyle
                    PrintStyle().stream(tail)

                # Clean up the filter
                agent.set_data(filter_key, None)
        except Exception as e:
            # If masking fails, proceed without masking
            pass

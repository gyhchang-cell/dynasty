package artifacts.config.display;

import artifacts.lang.LangEntry;

import java.util.List;

public record ConfigEntryDisplay(
        LangEntry title,
        List<LangEntry> description,
        int displayPriority
) {

}

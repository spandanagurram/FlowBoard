import ActivityCard from "./ActivityCard";

function ActivityTimeline({ activities }) {
  if (!activities.length) {
    return (
      <p className="text-slate-500">
        No activities found.
      </p>
    );
  }

  const groupedActivities = {};

  activities.forEach((activity) => {
    const activityDate = new Date(activity.created_at);
    const today = new Date();

    const activityDay = activityDate.toDateString();
    const todayDay = today.toDateString();

    let label = activityDate.toLocaleDateString(
      "en-GB",
      {
        day: "2-digit",
        month: "short",
        year: "numeric",
      }
    );

    if (activityDay === todayDay) {
      label = "Today";
    } else {
      const yesterday = new Date();
      yesterday.setDate(today.getDate() - 1);

      if (activityDay === yesterday.toDateString()) {
        label = "Yesterday";
      }
    }

    if (!groupedActivities[label]) {
      groupedActivities[label] = [];
    }

    groupedActivities[label].push(activity);
  });

  return (
    <div className="space-y-8">
      {Object.entries(groupedActivities).map(
        ([label, items]) => (
          <div
            key={label}
            className="space-y-4"
          >
            <h2 className="text-lg font-semibold">
              {label}
            </h2>

            <div className="space-y-3">
              {items.map((activity) => (
                <ActivityCard
                  key={activity.id}
                  activity={activity}
                />
              ))}
            </div>
          </div>
        )
      )}
    </div>
  );
}

export default ActivityTimeline;
from contracts.chunk import RetrievalResult


class RetrievalFilter:
    """Applies multi-tenant and role-based access control (RBAC) filtering."""

    @staticmethod
    def apply_access_filters(
        results: list[RetrievalResult],
        tenant_id: str,
        user_roles: list[str] | None = None,
    ) -> list[RetrievalResult]:
        filtered = []
        user_roles_set = set(user_roles or ["default", "viewer"])

        for item in results:
            # Enforce strict multi-tenant boundary
            chunk_tenant = item.metadata.get("tenant_id", "default")
            if chunk_tenant != tenant_id and chunk_tenant != "public":
                continue

            # Check ACL
            required_roles = item.metadata.get("allowed_roles")
            if required_roles and not any(r in user_roles_set for r in required_roles):
                continue

            filtered.append(item)
        return filtered
